"""Deterministic quota/lifecycle engine. Windows actions are injected separately.

R-F1: monotonic accounting; D017: exceptions are independent from normal usage.
An untrusted large reboot clock jump freezes the calendar until authenticated sync.
"""
from __future__ import annotations

from datetime import datetime, timezone, timedelta
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError


def timezone_for(name):
    try:
        return ZoneInfo(name)
    except ZoneInfoNotFoundError:
        if name in ("Asia/Ho_Chi_Minh", "Asia/Saigon"):
            return timezone(timedelta(hours=7))
        raise


class Enforcer:
    def __init__(self, store, policy, monotonic, wall_time):
        self.store, self.policy, self.monotonic = store, policy, monotonic
        self.previous_mono = monotonic()
        saved = store.get("trusted_time")
        if saved is None:
            # Production must seed trusted_time from pinned server before enforcement.
            raise ValueError("Authenticated server time required on first start")
        self.trusted = float(saved)
        self.clock_suspect = abs(wall_time() - self.trusted) > 300
        if not self.clock_suspect:
            self.trusted = max(self.trusted, wall_time())
        # A daily override keeps its signed deadline across reboot. Legacy
        # grants continue to end at restart, and neither can gain extra time.
        if self.store.get("override_mode") != "until_midnight":
            self.store.put("override_until", 0)
        self.wall_time = wall_time
        self.wall_offset = wall_time() - self.trusted
        if self.clock_suspect:
            self.store.clock_audit(self.trusted, wall_time())
        self.last_visible = None
        self.warnings = set()
        self.stopped = False

    def sync_time(self, timestamp):
        if timestamp < self.trusted - 300:
            raise ValueError("Server time rollback exceeds tolerance")
        self.trusted = max(self.trusted, float(timestamp))
        self.clock_suspect = False
        self.wall_offset = self.wall_time() - self.trusted
        self.store.put("trusted_time", self.trusted)

    def visible(self):
        self.last_visible = self.monotonic()

    def current_day(self):
        return datetime.fromtimestamp(self.trusted, timezone_for(self.policy["timezone"]))

    def usage(self, day=None):
        day = day or self.current_day().date().isoformat()
        row = self.store.db.execute("SELECT normal,exception FROM usage WHERE day=?", (day,)).fetchone()
        return row if row else (0.0, 0.0)

    def budget(self, day=None):
        now = self.current_day()
        day = day or now.date().isoformat()
        allocation = self.policy["allocation"]
        key = "weekend_sec" if datetime.fromisoformat(day).weekday() >= 5 else "weekday_sec"
        effective = allocation.get("effective_date", "0001-01-01")
        amount = allocation.get("previous_" + key, allocation[key]) if day < effective else allocation[key]
        limit = self.store.get("allocation_limit")
        if limit and day >= limit.get("effective_date", "0001-01-01"):
            amount = min(amount, limit[key])
        amount += self.store.get("extra:" + day, 0)
        amount -= self.store.get("reduced:" + day, 0)
        return max(0, amount)

    def reason(self):
        if self.stopped:
            return "tray_missing"
        if self.clock_suspect:
            return "clock_uncertain"
        if self.store.get("forced_lock", False):
            return "parent_lock"
        if self.store.get("override_until", 0) > self.trusted:
            return None
        now = self.current_day()
        if not self.policy["schedule"][now.weekday()][now.hour * 2 + now.minute // 30]:
            return "outside_schedule"
        if self.usage()[0] >= self.budget():
            return "quota_exhausted"
        return None

    def tick(self, *, locked=False, idle_seconds=0):
        current = self.monotonic()
        elapsed = current - self.previous_mono
        if elapsed < 0:
            raise ValueError("Monotonic clock went backwards")
        self.previous_mono = current
        # A tray lease cannot keep enforcement running after a crash/logoff.
        if self.last_visible is None or current - self.last_visible > 5:
            self.stopped = True
            return {"stop": True, "reason": "tray_missing", "warnings": []}
        notices = []
        # Process boundaries in one-second slices even after suspended worker scheduling.
        remaining = elapsed
        if elapsed > 5:
            # A suspend or stalled worker is not evidence of active usage.
            self.trusted += elapsed
            self.store.put("trusted_time", self.trusted)
            return {"stop": False, "reason": self.reason(), "warnings": [], "remaining_sec": max(0, self.budget() - self.usage()[0]), "clock_suspect": self.clock_suspect}
        with self.store.transaction() as db:
            while remaining > 0:
                step = min(1.0, remaining)
                reason = self.reason()
                day = self.current_day().date().isoformat()
                if reason is None and not locked and idle_seconds <= 300:
                    override = self.store.get("override_until", 0) > self.trusted
                    normal, exception = self.usage(day)
                    charge = min(step, self.store.get("override_until") - self.trusted) if override else min(step, max(0, self.budget(day) - normal))
                    db.execute("INSERT INTO usage(day,normal,exception) VALUES (?,?,?) ON CONFLICT(day) DO UPDATE SET normal=normal+excluded.normal, exception=exception+excluded.exception", (day, 0 if override else charge, charge if override else 0))
                    left = self.budget(day) - self.usage(day)[0]
                    for threshold in (600, 300, 60):
                        identity = (day, threshold)
                        if not override and normal < self.budget(day) and 0 < left <= threshold and normal < self.budget(day) - threshold <= normal + charge and identity not in self.warnings:
                            self.warnings.add(identity)
                            notices.append(threshold)
                self.trusted += step
                remaining -= step
            self.store.write(db, "trusted_time", self.trusted)
        if abs(self.wall_time() - self.trusted - self.wall_offset) > 300:
            if not self.clock_suspect:
                self.store.clock_audit(self.trusted, self.wall_time())
            self.clock_suspect = True
        return {"stop": False, "reason": self.reason(), "warnings": notices, "remaining_sec": max(0, self.budget() - self.usage()[0]), "clock_suspect": self.clock_suspect}

    def command(self, payload):
        """Call only after signature, device and expiration verification."""
        if payload["device_id"] != self.policy["device_id"]:
            raise ValueError("Wrong command target")
        sequence = payload["sequence"]
        with self.store.transaction() as db:
            last = self.store.get("command_sequence", 0)
            if db.execute("SELECT 1 FROM applied_commands WHERE id=?", (payload["id"],)).fetchone():
                return False
            expires = datetime.fromisoformat(payload["expires_at"].replace("Z", "+00:00")).timestamp()
            issued = datetime.fromisoformat(payload["issued_at"].replace("Z", "+00:00")).timestamp()
            if (expires <= self.trusted and payload["type"] not in ("delete_data", "reduce_budget")) or issued > self.trusted + 30:
                raise ValueError("Expired or future command")
            kind = payload["type"]
            if sequence <= last and kind in ("lock", "unlock"):
                # Record/ACK a delayed state command without resurrecting its effect.
                db.execute("INSERT INTO applied_commands VALUES (?,?)", (payload["id"], sequence))
                pending = self.store.get("pending_acks", [])
                self.store.write(db, "pending_acks", pending + [payload["id"]])
                return False
            seconds = payload.get("seconds", 900)
            daily_override = kind == "unlock" and payload.get("mode") == "until_midnight"
            if daily_override and not 0 < expires - issued <= 26 * 3600:
                raise ValueError("Daily override must end within the local day")
            if not daily_override and kind in ("unlock", "add_time") and (type(seconds) is not int or not 0 < seconds <= 900):
                raise ValueError("Grant must be at most 15 minutes")
            if kind == "lock":
                self.store.write(db, "forced_lock", True)
                self.store.write(db, "override_until", 0)
                self.store.write(db, "override_mode", None)
            elif kind == "unlock":
                self.store.write(db, "forced_lock", False)
                self.store.write(db, "override_until", expires if daily_override else min(issued + seconds, expires))
                self.store.write(db, "override_mode", "until_midnight" if daily_override else None)
            elif kind == "add_time":
                day = payload.get("day", self.current_day().date().isoformat())
                datetime.strptime(day, "%Y-%m-%d")
                self.store.write(db, "extra:" + day, self.store.get("extra:" + day, 0) + seconds)
            elif kind == "reduce_budget":
                allocation = dict(self.store.get("allocation_limit") or self.policy["allocation"])
                for key in ("weekday_sec", "weekend_sec"):
                    value = payload[key]
                    if type(value) is not int or not 0 <= value <= allocation[key]:
                        raise ValueError("Reduction cannot increase allocation")
                    allocation[key] = value
                allocation["effective_date"] = payload.get("effective_date", self.current_day().date().isoformat())
                allocation["policy_version"] = self.policy['version']
                self.store.write(db, "allocation_limit", allocation)
            elif kind == "delete_data":
                db.execute("DELETE FROM events")
                db.execute("DELETE FROM batches")
                db.execute("DELETE FROM usage")
                db.execute("DELETE FROM security_audit")
                db.execute("DELETE FROM state WHERE key NOT IN ('command_sequence','trusted_time','credentials_dpapi')")
                self.store.write(db, "deletion_generation", payload.get("generation", sequence))
                self.stopped = True
            else:
                raise ValueError("Unknown command")
            db.execute("INSERT INTO applied_commands VALUES (?,?)", (payload["id"], sequence))
            self.store.write(db, "command_sequence", max(last, sequence))
            pending = self.store.get("pending_acks", [])
            if payload["id"] not in pending:
                self.store.write(db, "pending_acks", pending + [payload["id"]])
        return True
