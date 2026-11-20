"""Durable daily counters for the shared entertainment quota and app groups."""
from datetime import datetime, timedelta, time

from agent.enforcer import timezone_for


class EntertainmentCounter:
    def __init__(self, store):
        self.store = store

    def used(self, day):
        return float(self.store.get('entertainment_usage', {}).get(day, 0))

    def group_used(self, day):
        return self.store.get('app_group_usage', {}).get(day, {})

    def exhausted(self, day, quota_sec, group=None):
        peer = self.store.get('entertainment_peer_usage', {})
        if peer.get('day') != day:
            peer = {}
        if group is None:
            return self.used(day) + peer.get('seconds', 0) >= quota_sec
        return self.group_used(day).get(group, 0) + peer.get('groups', {}).get(group, 0) >= quota_sec

    def sync_peer_usage(self, day, seconds, groups=None):
        with self.store.transaction() as db:
            if self.store.get('deletion_generation') is not None:
                return
            old = self.store.get('entertainment_peer_usage', {})
            if day >= old.get('day', ''):
                prior = old if old.get('day') == day else {}
                prior_groups = prior.get('groups', {})
                groups = groups or {}
                group_totals = {key: max(prior_groups.get(key, 0), groups.get(key, 0))
                                for key in prior_groups.keys() | groups.keys()}
                self.store.write(db, 'entertainment_peer_usage',
                                 {'day': day, 'seconds': max(seconds, prior.get('seconds', 0)), 'groups': group_totals})

    def record(self, name, seconds, timestamp, apps, timezone):
        # Match only a parent's explicit executable names. Suspends/stalls are
        # not active time; AppMonitor applies the same five-second ceiling.
        if name.casefold() in {app.casefold() for app in apps}:
            self.record_interval(seconds, timestamp, timezone, entertainment=True)

    def record_interval(self, seconds, timestamp, timezone, *, entertainment=False, group=None):
        if not 0 < seconds <= 5 or (not entertainment and group is None):
            return
        zone = timezone_for(timezone)
        end, cursor = timestamp, timestamp - seconds
        with self.store.transaction() as db:
            if self.store.get('deletion_generation') is not None:
                return
            values = self.store.get('entertainment_usage', {}) if entertainment else {}
            groups = self.store.get('app_group_usage', {}) if group is not None else {}
            while cursor < end:
                local = datetime.fromtimestamp(cursor, zone)
                midnight = datetime.combine(local.date() + timedelta(days=1), time(), zone).timestamp()
                charge = min(end, midnight) - cursor
                day = local.date().isoformat()
                if entertainment:
                    values[day] = min(86400, values.get(day, 0) + charge)
                if group is not None:
                    daily = groups.setdefault(day, {})
                    daily[group] = min(86400, daily.get(group, 0) + charge)
                cursor += charge
            cutoff = (datetime.fromtimestamp(end, zone).date() - timedelta(days=90)).isoformat()
            if entertainment:
                self.store.write(db, 'entertainment_usage', {d: v for d, v in values.items() if d >= cutoff})
            if group is not None:
                self.store.write(db, 'app_group_usage', {d: v for d, v in groups.items() if d >= cutoff})
