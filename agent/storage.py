"""Durable cache and transport metadata; event payloads remain exactly seven fields."""
from __future__ import annotations

import json
import sqlite3
import time
import threading
import uuid
from contextlib import contextmanager
from pathlib import Path
from datetime import datetime, timezone

EVENT_FIELDS = frozenset({"ts", "device_id", "child_id", "type", "subject", "duration_sec", "policy_id"})
EVENT_TYPES = frozenset({"app_start", "app_stop", "domain_query", "blocked_app", "blocked_domain", "quota_warning", "locked", "unlock_request", "override_granted"})


class QueueFull(RuntimeError):
    pass


class Store:
    def __init__(self, path: str | Path, max_events: int = 100_000):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.max_events = max_events
        self.lock = threading.RLock()
        self.db = sqlite3.connect(self.path, timeout=10, check_same_thread=False)
        self.db.execute("PRAGMA journal_mode=WAL")
        self.db.execute("PRAGMA synchronous=FULL")
        self.db.execute("PRAGMA secure_delete=ON")
        self.db.executescript("""
            CREATE TABLE IF NOT EXISTS state (key TEXT PRIMARY KEY, value TEXT NOT NULL);
            CREATE TABLE IF NOT EXISTS usage (day TEXT PRIMARY KEY, normal REAL NOT NULL DEFAULT 0, exception REAL NOT NULL DEFAULT 0);
            CREATE TABLE IF NOT EXISTS events (id INTEGER PRIMARY KEY, payload TEXT NOT NULL, created REAL NOT NULL);
            CREATE TABLE IF NOT EXISTS batches (key TEXT PRIMARY KEY, ids TEXT NOT NULL, payload TEXT NOT NULL);
            CREATE TABLE IF NOT EXISTS applied_commands (id TEXT PRIMARY KEY, sequence INTEGER UNIQUE NOT NULL);
            CREATE TABLE IF NOT EXISTS security_audit (id INTEGER PRIMARY KEY, ts REAL NOT NULL, category TEXT NOT NULL, details TEXT NOT NULL);
        """)
        self.db.commit()

    @contextmanager
    def transaction(self):
        with self.lock:
            try:
                self.db.execute("BEGIN IMMEDIATE")
                yield self.db
                self.db.commit()
            except BaseException:
                self.db.rollback()
                raise

    def get(self, key, default=None):
        with self.lock:
            row = self.db.execute("SELECT value FROM state WHERE key=?", (key,)).fetchone()
            return json.loads(row[0]) if row else default

    def put(self, key, value):
        with self.transaction() as db:
            self.write(db, key, value)

    @staticmethod
    def write(db, key, value):
        db.execute("INSERT INTO state VALUES (?,?) ON CONFLICT(key) DO UPDATE SET value=excluded.value", (key, json.dumps(value, separators=(",", ":"))))

    def queue(self, event: dict, *, state_updates=None):
        if set(event) != EVENT_FIELDS or event["type"] not in EVENT_TYPES:
            raise ValueError("Event must have exactly the seven permitted fields and a permitted type")
        if not isinstance(event["subject"], str) or any(x in event["subject"] for x in ("://", "?", "#", "\\", "/")):
            raise ValueError("Event subject cannot contain a URL or path")
        if type(event["duration_sec"]) is not int or not 0 <= event["duration_sec"] <= 86400:
            raise ValueError("Invalid event duration")
        timestamp = datetime.fromisoformat(event['ts'].replace('Z', '+00:00'))
        if timestamp.tzinfo is None:
            raise ValueError('Event timestamp must include timezone')
        with self.transaction() as db:
            if self.get('deletion_generation') is not None:
                return False
            if db.execute("SELECT count(*) FROM events").fetchone()[0] >= self.max_events:
                raise QueueFull("Event buffer full: stop collection and display a visible warning")
            db.execute("INSERT INTO events(payload,created) VALUES (?,?)", (json.dumps(event, separators=(",", ":")), timestamp.timestamp()))
            for key, value in (state_updates or {}).items():
                self.write(db, key, value)
            return True

    def batch(self, limit=100):
        if not 1 <= limit <= 500:
            raise ValueError("Invalid batch limit")
        with self.transaction() as db:
            pending = db.execute("SELECT key,payload FROM batches LIMIT 1").fetchone()
            if pending:
                return pending[0], json.loads(pending[1])
            rows = db.execute("SELECT id,payload FROM events ORDER BY id LIMIT ?", (limit,)).fetchall()
            if not rows:
                return None
            key = str(uuid.uuid4())
            payload = [json.loads(row[1]) for row in rows]
            db.execute("INSERT INTO batches VALUES (?,?,?)", (key, json.dumps([r[0] for r in rows]), json.dumps(payload)))
            return key, payload

    def acknowledge_batch(self, key):
        with self.transaction() as db:
            row = db.execute("SELECT ids FROM batches WHERE key=?", (key,)).fetchone()
            if row:
                db.executemany("DELETE FROM events WHERE id=?", [(i,) for i in json.loads(row[0])])
                db.execute("DELETE FROM batches WHERE key=?", (key,))

    def delete_child_data(self, generation):
        """Delete queued and in-flight data before acknowledging deletion to server."""
        with self.transaction() as db:
            db.execute("DELETE FROM events")
            db.execute("DELETE FROM batches")
            self.write(db, "deletion_generation", generation)

    def prune(self, now=None):
        with self.transaction() as db:
            # Do not mutate an in-flight idempotent batch: expire that batch as a unit.
            cutoff = (time.time() if now is None else now) - 90 * 86400
            expired = {r[0] for r in db.execute("SELECT id FROM events WHERE created<?", (cutoff,))}
            for key, ids_json in db.execute("SELECT key,ids FROM batches").fetchall():
                ids = json.loads(ids_json)
                if expired.intersection(ids):
                    db.executemany("DELETE FROM events WHERE id=?", [(i,) for i in ids])
                    db.execute("DELETE FROM batches WHERE key=?", (key,))
            db.execute("DELETE FROM events WHERE created<?", (cutoff,))
            db.execute("DELETE FROM security_audit WHERE ts<?", (cutoff,))
            cutoff_day = datetime.fromtimestamp(cutoff, timezone.utc).date().isoformat()
            view = self.get('child_view')
            if view:
                if view.get('day', '') < cutoff_day:
                    view = {'name': view.get('name', ''), 'audit': view.get('audit', [])}
                view['audit'] = [item for item in view.get('audit', []) if item.get('ts', '') >= datetime.fromtimestamp(cutoff, timezone.utc).isoformat()]
                if (view.get('last_request') or {}).get('ts', '') < datetime.fromtimestamp(cutoff, timezone.utc).isoformat():
                    view.pop('last_request', None)
                self.write(db, 'child_view', view)
            if (self.get('time_request') or {}).get('created', cutoff) < cutoff:
                db.execute("DELETE FROM state WHERE key='time_request'")
            db.execute("DELETE FROM usage WHERE day<?", (cutoff_day,))
            for key, in db.execute("SELECT key FROM state WHERE key LIKE 'extra:%' OR key LIKE 'reduced:%'").fetchall():
                if key.split(':', 1)[1] < cutoff_day:
                    db.execute('DELETE FROM state WHERE key=?', (key,))

    def clock_audit(self, trusted_time, local_time):
        """Purpose-limited local security metadata, not a tenth activity event type."""
        with self.transaction() as db:
            db.execute("INSERT INTO security_audit(ts,category,details) VALUES (?,?,?)", (trusted_time, "clock_discontinuity", json.dumps({"drift_sec": round(local_time - trusted_time, 3)})))

    def close(self):
        with self.lock:
            self.db.execute("PRAGMA wal_checkpoint(TRUNCATE)")
            self.db.close()
