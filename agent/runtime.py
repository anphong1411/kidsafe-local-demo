"""Service coordinator. Only an explicitly configured child lab may enforce policy."""
from __future__ import annotations

import base64
from datetime import datetime, timezone
import json
from pathlib import Path
import queue
import threading
import time
import uuid
import subprocess

from agent.dns_proxy import DNSProxy, Resolver
from agent.enforcer import Enforcer
from agent.ipc import TrayIPC
from agent.policy import verify_envelope
from agent.storage import Store
from agent.sync import DeviceSync
from agent.transport import PinnedHTTPS, HTTPFailure
from agent.windows import unprotect_secret, verify_tray_peer
from agent.apps import AppMonitor, AppRules
from agent.app_groups import AppGroups
from agent.entertainment import EntertainmentCounter


class Runtime:
    def __init__(self, config_path, stop=None):
        self.config_path = Path(config_path).resolve()
        self.config = json.loads(self.config_path.read_text(encoding='utf-8-sig'))
        if self.config.get('lab_enforcement') is not True:
            raise ValueError('Child lab configuration required')
        self.stop = stop or threading.Event()
        self.store = Store(self.config['database'])
        encrypted = self.store.get('credentials_dpapi')
        self.cleanup_complete = self.store.get('deletion_generation') is not None and not encrypted
        if self.cleanup_complete:
            self.cleanup_pending = True
            return
        credentials = json.loads(unprotect_secret(base64.b64decode(encrypted))) if encrypted else {}
        self.transport = PinnedHTTPS(self.config['server_url'], self.config['ca_file'], self.config['certificate_pin'])
        self.sync = DeviceSync(self.store, self.transport, credentials, self.config['signing_public_key'])
        if not encrypted:
            response = self.sync.enroll(self.config['enrollment_code'], self.config['fingerprint'], self.config['device_name'])
            self.sync.persist_credentials()  # Current service identity DPAPI, never child-readable.
            snapshot = {'device_id': credentials['device_id'], 'status': 'tray_unavailable',
                        'quota_used_sec': 0, 'exception_used_sec': 0,
                        'policy_version': response['policy']['payload']['version'],
                        'usage_date': datetime.now(timezone.utc).date().isoformat()}
            trusted = self.sync.call('POST', '/api/device/heartbeat', snapshot)['server_time']
            self.store.put('trusted_time', datetime.fromisoformat(trusted).timestamp())
        if self.store.get('trusted_time') is None:
            # Recover a crash after enrollment persisted credentials but before time sync.
            envelope = self.store.get('policy_envelope')
            response = self.sync.call('POST', '/api/device/heartbeat', {
                'device_id': credentials['device_id'], 'status': 'tray_unavailable',
                'quota_used_sec': 0, 'policy_version': envelope['payload']['version'],
                'usage_date': datetime.now(timezone.utc).date().isoformat()})
            self.store.put('trusted_time', datetime.fromisoformat(response['server_time']).timestamp())
        if self.config.pop('enrollment_code', None):
            pending_config = self.config_path.with_suffix('.new')
            pending_config.write_text(json.dumps(self.config, indent=2), encoding='utf-8')
            pending_config.replace(self.config_path)
        self.cleanup_pending = self.store.get('deletion_generation') is not None
        if self.cleanup_pending:
            return
        envelope = self.store.get('policy_envelope')
        self.policy = verify_envelope(envelope, self.config['signing_public_key'], credentials['device_id'])
        self.engine = Enforcer(self.store, self.policy, time.monotonic, time.time)
        self.guard = threading.RLock()
        self.monitor_guard = threading.Lock()
        self.snapshot = {'stop': False, 'reason': None, 'warnings': []}
        self.observation = {'locked': True, 'idle_seconds': 301}
        self.ipc = None
        self.dns = None
        self.dns_v6 = None
        self.explanation = None
        self.explanation_ack = None
        self.tray_pid = None
        self.entertainment = EntertainmentCounter(self.store)
        self.app_groups = AppGroups(self.policy)
        self.monitor = AppMonitor(
            self.config['child_username'], AppRules(self.policy['app_mode'], self.policy['apps']),
            self.event, self.explain, on_usage=self.record_group_usage,
            group_block=self.group_block, explain_group=self.explain_group,
        )

    def record_group_usage(self, name, digest, elapsed):
        if digest is None:
            return
        with self.guard:
            groups = self.app_groups.matches(name, digest)
            if groups:
                group = groups[0]
                self.entertainment.record_interval(
                    elapsed, self.engine.trusted, self.policy['timezone'], group=group,
                    entertainment=self.app_groups.mode(group) == 'entertainment',
                )

    def group_block(self, name, digest):
        with self.guard:
            return self.app_groups.block_notice(name, digest, self.engine.current_day(), self.entertainment)

    def event(self, kind, subject='', duration=0):
        # Windows filenames can contain URL punctuation; retain a safe app label,
        # never let an executable filename poison the strict event queue schema.
        subject = ''.join('_' if char in '/\\?#:@' or ord(char) < 32 else char for char in str(subject))[:253]
        self.store.queue({'ts': datetime.fromtimestamp(self.engine.trusted, timezone.utc).isoformat(),
                          'device_id': self.sync.credentials['device_id'],
                          'child_id': self.sync.credentials['child_id'], 'type': kind,
                          'subject': subject, 'duration_sec': int(duration),
                          'policy_id': str(self.policy.get('policy_id', self.policy['version']))})

    def lease(self, payload):
        idle = payload.get('idle_seconds')
        if type(payload.get('locked')) is not bool or type(idle) not in (int, float) or not 0 <= idle <= 2**32:
            raise ValueError('Invalid session observation')
        with self.guard:
            self.observation = {'locked': payload['locked'], 'idle_seconds': idle}
            foreground = payload.get('foreground_pid')
            if type(foreground) is not int or foreground < 0:
                raise ValueError('Invalid foreground process')
            self.foreground_pid = foreground
            self.tray_pid = payload['pid']
            self.explanation_ack = payload.get('explanation_ack')
            self.engine.visible()

    def status(self):
        with self.guard:
            result = dict(self.snapshot)
            result['child_view'] = self.child_view()
            if self.explanation:
                result['explanation'] = {key: self.explanation[key] for key in ('id', 'subject', 'text')}
            self.snapshot['warnings'] = []
            return result

    def child_view(self):
        day = self.engine.current_day().date().isoformat()
        normal, _ = self.engine.usage()
        cached = self.store.get('child_view', {})
        if cached.get('day') != day:
            cached = {'name': cached.get('name', ''), 'top_apps': [], 'top_domains': [], 'audit': cached.get('audit', [])}
        peer = self.store.get('entertainment_peer_usage', {})
        entertainment_used = self.entertainment.used(day) + (peer.get('seconds', 0) if peer.get('day') == day else 0)
        requested = self.store.get('time_request')
        if requested and requested.get('day') != day:
            requested = None
        server_request = cached.get('last_request')
        if requested and server_request and server_request.get('ts') == requested['ts']:
            requested = {**requested, 'status': server_request['status']}
        return {**cached, 'day': day, 'timezone': self.policy['timezone'], 'remaining_sec': max(0, int(self.engine.budget() - normal)),
                'budget_sec': int(self.engine.budget()), 'entertainment_quota_sec': self.policy.get('entertainment_quota_sec', 0),
                'entertainment_remaining_sec': max(0, int(self.policy.get('entertainment_quota_sec', 0) - entertainment_used)),
                'reason': self.engine.reason(), 'request': requested,
                'override_active': self.store.get('override_until', 0) > self.engine.trusted and self.engine.reason() is None,
                'offline': self.engine.trusted - self.store.get('child_view_synced', 0) > 75}

    def request_time(self, minutes):
        if type(minutes) is not int or minutes not in (5, 10, 15):
            raise ValueError('Choose 5, 10 or 15 minutes')
        with self.guard:
            current = self.child_view().get('request')
            if current and current['status'] != 'acknowledged' and self.engine.trusted - current['created'] < 600:
                return {'queued': False, 'pending': True}
            ts = datetime.fromtimestamp(self.engine.trusted, timezone.utc).isoformat()
            metadata = {'ts': ts, 'day': self.engine.current_day().date().isoformat(),
                        'created': self.engine.trusted, 'minutes': minutes, 'status': 'queued'}
            event = {'ts': ts, 'device_id': self.sync.credentials['device_id'],
                     'child_id': self.sync.credentials['child_id'], 'type': 'unlock_request',
                     'subject': 'more_time', 'duration_sec': minutes * 60,
                     'policy_id': str(self.policy.get('policy_id', self.policy['version']))}
            queued = self.store.queue(event, state_updates={'time_request': metadata})
            return {'queued': bool(queued), 'offline': self.child_view()['offline']}

    def explain(self, subject):
        with self.guard:
            return self._explain(subject)

    def explain_group(self, subject, message):
        with self.guard:
            return self._explain(subject, message)

    def _explain(self, subject, message=None):
        text = message or f'Ứng dụng {subject} đang nằm trong danh sách chưa được phép. Em có thể hỏi phụ huynh để thay đổi quy định nhé.'
        same_notice = self.explanation and self.explanation['subject'] == subject and self.explanation['text'] == text
        if self.explanation and not same_notice and time.monotonic() > self.explanation['deadline']:
            # The previous process may have closed or become allowed before ACK.
            self.explanation = self.explanation_ack = None
        if self.explanation:
            if not same_notice:
                return None
            if self.explanation_ack == self.explanation['id']:
                self.explanation = None
                self.explanation_ack = None
                return True
            if time.monotonic() > self.explanation['deadline']:
                return False
            return None
        self.explanation = {'id': str(uuid.uuid4()), 'subject': subject, 'text': text,
                            'deadline': time.monotonic() + 4}
        return None

    def dns_start(self):
        resolver = Resolver(self.policy['blocked_domains'], tuple(self.config['upstream']),
                            safesearch=self.policy['safesearch'],
                            block_doh=self.config.get('block_doh', False),
                            on_query=lambda domain, blocked: self.event('blocked_domain' if blocked else 'domain_query', domain))
        self.dns = DNSProxy(resolver).start()
        try:
            self.dns_v6 = DNSProxy(resolver, host='::1').start()
        except BaseException:
            self.dns.stop()
            self.dns = None
            raise

    def dns_configuration(self, action):
        if not self.config.get('manage_dns', False):
            return
        script = Path(__file__).resolve().parent / 'scripts' / 'Manage-LabDns.ps1'
        subprocess.run(['powershell.exe', '-NoProfile', '-NonInteractive', '-ExecutionPolicy', 'Bypass', '-File', str(script), '-Action', action,
                        '-Snapshot', self.config['dns_snapshot'], '-InterfaceIndices', ','.join(map(str, self.config['dns_interfaces']))], check=True, timeout=30, creationflags=getattr(subprocess, 'CREATE_NO_WINDOW', 0), capture_output=True)

    def heartbeat(self):
        with self.guard:
            normal, exception = self.engine.usage()
            day = self.engine.current_day().date().isoformat()
            return {'device_id': self.sync.credentials['device_id'],
                    'status': 'locked' if self.observation['locked'] or self.engine.reason() else ('idle' if self.observation['idle_seconds'] > 300 else 'active'),
                    'quota_used_sec': int(normal), 'exception_used_sec': int(exception),
                    'entertainment_used_sec': int(self.entertainment.used(day)),
                    'group_used_sec': {key: int(seconds) for key, seconds in self.entertainment.group_used(day).items()},
                    'policy_version': self.policy['version'],
                    'usage_date': day}

    def browser_configuration(self, action):
        if not self.config.get('manage_browser_doh', False):
            return
        script = Path(__file__).resolve().parent / 'scripts' / 'Manage-LabBrowserPolicy.ps1'
        subprocess.run(['powershell.exe', '-NoProfile', '-NonInteractive', '-ExecutionPolicy', 'Bypass', '-File', str(script), '-Action', action,
                        '-Snapshot', self.config['browser_policy_snapshot'], '-ChildLab'], check=True, timeout=30,
                       creationflags=getattr(subprocess, 'CREATE_NO_WINDOW', 0), capture_output=True)

    def restore_network_configuration(self):
        errors = []
        for operation in (self.dns_configuration, self.browser_configuration):
            try:
                operation('Restore')
            except Exception as error:
                errors.append(error)
        if errors:
            raise RuntimeError('Could not restore all child-lab network settings; snapshots retained') from errors[0]

    def network(self):
        while not self.stop.is_set():
            try:
                self.sync.heartbeat(self.heartbeat())
                view = self.sync.call('GET', '/api/device/child-view')
                with self.guard:
                    if self.store.get('deletion_generation') is None:
                        with self.store.transaction() as db:
                            self.store.write(db, 'child_view', view)
                            self.store.write(db, 'child_view_synced', self.engine.trusted)
            except Exception:
                # Offline keeps signed policy/allocations. No secrets in logs.
                pass
            try:
                # Retention also runs offline; transparency snapshots must not
                # keep old activity indefinitely while the server is unreachable.
                self.store.prune(now=self.engine.trusted)
            except Exception:
                pass
            self.stop.wait(30)  # bounded below the 60s policy delivery requirement

    def apps_worker(self):
        try:
            while not self.stop.wait(.5):
                with self.guard:
                    foreground_pid = getattr(self, 'foreground_pid', 0)
                    locked = self.observation['locked']
                    active = not self.observation['locked'] and self.observation['idle_seconds'] <= 300 and not self.engine.reason()
                    tray_pid = self.tray_pid
                # First-time hashes can be expensive; never stall tray leases or
                # the monotonic quota loop while reading executable files.
                with self.monitor_guard:
                    self.monitor.tick(foreground_pid, active=active, tray_pid=tray_pid, enforce=not locked)
        except Exception:
            with self.guard:
                self.snapshot = {'stop': True, 'reason': 'app_monitor_unavailable', 'warnings': []}
            self.stop.set()

    def apply_incoming(self):
        while True:
            try:
                kind, payload = self.sync.incoming.get_nowait()
            except queue.Empty:
                return
            if kind == 'time':
                self.engine.sync_time(payload)
            elif kind == 'entertainment_usage':
                self.entertainment.sync_peer_usage(*payload)
            elif kind == 'policy':
                limit = self.store.get('allocation_limit')
                if limit and payload['version'] > limit.get('policy_version', 0) and all(payload['allocation'][key] == limit[key] for key in ('weekday_sec', 'weekend_sec')):
                    self.store.put('allocation_limit', None)
                self.policy = self.engine.policy = payload
                self.monitor.rules = AppRules(self.policy['app_mode'], self.policy['apps'])
                self.app_groups = AppGroups(payload)
                if self.dns:
                    self.dns.stop()
                    if self.dns_v6:
                        self.dns_v6.stop()
                    self.dns_start()
            elif kind == 'command':
                applied = self.engine.command(payload)
                if applied and payload['type'] == 'unlock':
                    self.event('override_granted', 'parent_override')
                if payload['type'] == 'delete_data':
                    # Preserve only cleanup credentials until the server confirms ACK.
                    self.stop.set()
                    self.acknowledge_deletion(payload['id'])

    def acknowledge_deletion(self, command_id):
        try:
            self.sync.call('POST', '/api/device/commands/' + command_id + '/ack', {})
        except HTTPFailure as error:
            # A committed deletion ACK revokes tokens. If its response was lost,
            # that permanent revocation is safe evidence to finish local cleanup.
            if error.status not in (401, 403, 404, 410):
                raise
        with self.store.transaction() as db:
            self.store.write(db, 'pending_acks', [])
            self.store.write(db, 'credentials_dpapi', None)

    def run(self):
        if self.cleanup_pending:
            try:
                if not self.cleanup_complete:
                    row = self.store.db.execute('SELECT id FROM applied_commands ORDER BY sequence DESC LIMIT 1').fetchone()
                    if row:
                        self.acknowledge_deletion(row[0])
            finally:
                self.store.close()
            return
        config = self.config
        self.ipc = TrayIPC(config['ipc_token'], self.status, self.lease,
                           self.request_time, port=config.get('ipc_port', 17843),
                           verify_peer=lambda payload, address: verify_tray_peer(payload, address,
                               port=config.get('ipc_port', 17843), python_exe=config['tray_python'],
                               tray_script=config['tray_script'], tray_config=config['tray_config'],
                               username=config['child_username'], base_python=config.get('tray_base_python')))
        workers = []
        try:
            self.ipc.start()
            # Recover prior settings if a previous service process was killed.
            self.restore_network_configuration()
            # No DNS or enforcement until authenticated visible tray has checked in.
            deadline = time.monotonic() + 15
            while self.engine.last_visible is None and time.monotonic() < deadline and not self.stop.wait(.1):
                pass
            if self.engine.last_visible is None:
                return
            self.dns_start()
            self.dns_configuration('Apply')
            self.browser_configuration('Apply')
            for target in (self.network, self.sync.websocket, self.apps_worker):
                thread = threading.Thread(target=target, daemon=True)
                thread.start()
                workers.append(thread)
            previous_reason = None
            while not self.stop.wait(.5):
                with self.guard:
                    self.apply_incoming()
                    if self.stop.is_set():
                        break
                    self.snapshot = self.engine.tick(**self.observation)
                    if self.snapshot['stop']:
                        break
                    for warning in self.snapshot['warnings']:
                        self.event('quota_warning', str(warning))
                    if self.snapshot['reason'] and self.snapshot['reason'] != previous_reason:
                        self.event('locked', self.snapshot['reason'])
                    previous_reason = self.snapshot['reason']
        finally:
            self.stop.set()
            self.sync.stop_event.set()
            try:
                # Flush foreground accounting only after the worker has stopped.
                if self.monitor_guard.acquire(timeout=12):
                    try:
                        if self.store.get('deletion_generation') is None:
                            self.monitor.close()
                    finally:
                        self.monitor_guard.release()
            finally:
                try:
                    self.restore_network_configuration()
                finally:
                    if self.dns:
                        self.dns.stop()
                    if self.dns_v6:
                        self.dns_v6.stop()
                    if self.ipc:
                        self.ipc.stop()
                    for worker in workers:
                        worker.join(12)
                    if all(not worker.is_alive() for worker in workers):
                        self.store.close()
