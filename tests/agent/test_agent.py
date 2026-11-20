import base64
import hashlib
import json
import socket
import struct
import http.client
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone, timedelta

import pytest
from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from dnslib import A, DNSRecord, QTYPE, RCODE, RR

from agent.apps import AppMonitor, AppRules, ExecutableHasher, terminate_verified
from agent.dns_proxy import DNSProxy, Resolver, event_domain, matches
from agent.enforcer import Enforcer
from agent.policy import canonical, install_policy
from agent.storage import QueueFull, Store
from agent.ipc import TrayIPC
from agent.runtime import Runtime
from agent.transport import HTTPFailure
import threading


@pytest.fixture
def store(tmp_path):
    result = Store(tmp_path / "cache.sqlite3")
    yield result
    result.close()


@pytest.fixture
def policy():
    return {"policy_id": "p1", "device_id": "d1", "child_id": "c1", "version": 1, "timezone": "Asia/Ho_Chi_Minh", "schedule": [[True] * 48 for _ in range(7)], "allocation": {"weekday_sec": 180, "weekend_sec": 180}}


def event(kind="domain_query"):
    return {"ts": "2026-11-04T00:00:00Z", "device_id": "d1", "child_id": "c1", "type": kind, "subject": "example.com", "duration_sec": 0, "policy_id": "p1"}


class Clock:
    def __init__(self):
        self.mono = 0
        self.wall = datetime(2026, 11, 4, 3, tzinfo=timezone.utc).timestamp()
    def advance(self, seconds):
        self.mono += seconds
        self.wall += seconds


def engine(store, policy):
    clock = Clock()
    store.put("trusted_time", clock.wall)
    result = Enforcer(store, policy, lambda: clock.mono, lambda: clock.wall)
    result.visible()
    return result, clock


def step(enforcer, clock, seconds=1, **kwargs):
    clock.advance(seconds)
    enforcer.visible()
    return enforcer.tick(**kwargs)


def command(enforcer, kind, sequence=1, **extra):
    start = datetime.fromtimestamp(enforcer.trusted, timezone.utc)
    return {"id": str(sequence), "sequence": sequence, "type": kind, "device_id": "d1", "issued_at": start.isoformat(), "expires_at": (start + timedelta(seconds=900)).isoformat(), "seconds": 900, **extra}


def test_signed_policy_tamper_and_rollback(store, policy):
    private = Ed25519PrivateKey.generate()
    key = base64.b64encode(private.public_key().public_bytes(serialization.Encoding.Raw, serialization.PublicFormat.Raw)).decode()
    def signed(payload):
        return {"payload": json.loads(json.dumps(payload)), "signature": base64.b64encode(private.sign(canonical(payload))).decode()}
    envelope = signed(policy)
    assert install_policy(store, envelope, key, "d1")["version"] == 1
    envelope["payload"]["allocation"]["weekday_sec"] = 999
    with pytest.raises(InvalidSignature):
        install_policy(store, envelope, key, "d1")
    policy["version"] = 0
    with pytest.raises(ValueError, match="rollback"):
        install_policy(store, signed(policy), key, "d1")


def test_policy_rejects_same_version_different_content(store, policy):
    private = Ed25519PrivateKey.generate()
    key = base64.b64encode(private.public_key().public_bytes(serialization.Encoding.Raw, serialization.PublicFormat.Raw)).decode()
    def signed():
        return {"payload": json.loads(json.dumps(policy)), "signature": base64.b64encode(private.sign(canonical(policy))).decode()}
    install_policy(store, signed(), key, "d1")
    policy["allocation"]["weekday_sec"] = 181
    with pytest.raises(ValueError, match="Same version"):
        install_policy(store, signed(), key, "d1")


def test_exact_event_schema_and_types(store):
    store.queue(event())
    for invalid in ({**event(), "extra": 1}, {**event(), "type": "screenshot"}, {**event(), "subject": "https://example.com/secret"}):
        with pytest.raises(ValueError):
            store.queue(invalid)


def test_retry_batch_identity_durable(tmp_path):
    path = tmp_path / "cache.db"
    first = Store(path)
    first.queue(event())
    batch = first.batch()
    first.close()
    second = Store(path)
    assert second.batch() == batch
    second.acknowledge_batch(batch[0])
    assert second.batch() is None
    second.close()


def test_queue_full_preserves_events(tmp_path):
    result = Store(tmp_path / "queue.db", max_events=1)
    result.queue(event())
    with pytest.raises(QueueFull):
        result.queue(event())
    assert len(result.batch()[1]) == 1
    result.close()


def test_concurrent_queue_transactions(store):
    with ThreadPoolExecutor(max_workers=8) as pool:
        list(pool.map(lambda i: store.queue(event()), range(100)))
    assert len(store.batch()[1]) == 100


def test_retention_preserves_unrelated_inflight_batch(store):
    store.queue(event())
    batch = store.batch()
    with store.transaction() as db:
        db.execute("INSERT INTO events(payload,created) VALUES (?,?)", (json.dumps(event()), 0))
    store.prune()
    assert store.batch() == batch


def test_deletion_cancels_inflight(store):
    store.queue(event())
    store.batch()
    store.delete_child_data(4)
    assert store.batch() is None
    assert store.get("deletion_generation") == 4


def test_three_minute_quota_and_warning_no_extra_grace(store, policy):
    enforcer, clock = engine(store, policy)
    warnings = []
    for _ in range(180):
        result = step(enforcer, clock)
        warnings.extend(result["warnings"])
    assert enforcer.usage() == (180, 0)
    assert result["reason"] == "quota_exhausted"
    assert warnings == [60]
    step(enforcer, clock)
    assert enforcer.usage() == (180, 0)


def test_schedule_idle_and_locked(store, policy):
    enforcer, clock = engine(store, policy)
    step(enforcer, clock, locked=True)
    step(enforcer, clock, idle_seconds=301)
    assert enforcer.usage() == (0, 0)
    policy["schedule"] = [[False] * 48 for _ in range(7)]
    assert step(enforcer, clock)["reason"] == "outside_schedule"
    assert enforcer.usage() == (0, 0)


def test_tray_missing_stops_before_accounting(store, policy):
    enforcer, clock = engine(store, policy)
    clock.advance(6)
    assert enforcer.tick()["stop"]
    assert enforcer.usage() == (0, 0)


def test_backward_clock_does_not_give_quota(store, policy):
    enforcer, clock = engine(store, policy)
    step(enforcer, clock)
    clock.wall -= 3 * 3600
    result = step(enforcer, clock)
    assert result["clock_suspect"]
    assert result["reason"] == "clock_uncertain"
    assert enforcer.usage()[0] <= 2
    audit = store.db.execute('SELECT category,details FROM security_audit').fetchall()
    assert len(audit) == 1
    assert audit[0][0] == 'clock_discontinuity'
    assert abs(json.loads(audit[0][1])['drift_sec'] + 10800) <= 1
    enforcer.sync_time(enforcer.trusted)
    assert enforcer.usage()[0] <= 2


def test_unlock_separate_budget_and_lock_cancels_replay(store, policy):
    policy["schedule"] = [[False] * 48 for _ in range(7)]
    enforcer, clock = engine(store, policy)
    unlock = command(enforcer, "unlock")
    assert enforcer.command(unlock)
    assert not enforcer.command(unlock)
    step(enforcer, clock)
    assert enforcer.usage() == (0, 1)
    assert enforcer.command(command(enforcer, "lock", 2))
    assert enforcer.reason() == "parent_lock"
    assert not enforcer.command(unlock)


def test_add_time_does_not_bypass_schedule(store, policy):
    enforcer, clock = engine(store, policy)
    policy["schedule"] = [[False] * 48 for _ in range(7)]
    grant = command(enforcer, "add_time", day=enforcer.current_day().date().isoformat())
    enforcer.command(grant)
    assert enforcer.budget() == 1080
    assert enforcer.reason() == "outside_schedule"
    assert not enforcer.command(grant)
    assert enforcer.budget() == 1080


def test_reboot_never_restarts_exception(store, policy):
    enforcer, clock = engine(store, policy)
    enforcer.command(command(enforcer, "unlock"))
    other = Enforcer(store, policy, lambda: clock.mono, lambda: clock.wall)
    assert store.get("override_until") == 0


def test_daily_unlock_lasts_until_midnight_and_keeps_signed_deadline_on_restart(store, policy):
    policy["schedule"] = [[False] * 48 for _ in range(7)]
    enforcer, clock = engine(store, policy)
    midnight = enforcer.current_day().replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=1)
    unlock = command(enforcer, "unlock", mode="until_midnight", expires_at=midnight.isoformat())
    assert enforcer.command(unlock)
    step(enforcer, clock, seconds=901)
    assert enforcer.reason() is None
    restarted = Enforcer(store, policy, lambda: clock.mono, lambda: clock.wall)
    step(restarted, clock)
    assert restarted.usage() == (0, 1)
    step(restarted, clock, seconds=midnight.timestamp() - restarted.trusted)
    assert restarted.reason() == "outside_schedule"
    assert not restarted.command(unlock)


def test_lock_cancels_daily_unlock(store, policy):
    enforcer, _ = engine(store, policy)
    midnight = enforcer.current_day().replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=1)
    unlock = command(enforcer, "unlock", mode="until_midnight", expires_at=midnight.isoformat())
    assert enforcer.command(unlock)
    assert enforcer.command(command(enforcer, "lock", sequence=2))
    assert enforcer.reason() == "parent_lock"
    assert not enforcer.command(unlock)


def test_budget_return_durable_without_usage_reset(store, policy):
    enforcer, clock = engine(store, policy)
    step(enforcer, clock)
    enforcer.command(command(enforcer, "reduce_budget", weekday_sec=30, weekend_sec=20))
    assert enforcer.budget() == 30
    assert enforcer.usage() == (1, 0)
    with pytest.raises(ValueError):
        enforcer.command(command(enforcer, "reduce_budget", 2, weekday_sec=31, weekend_sec=20))


def test_app_hash_rename_and_spoofed_allow_name(tmp_path):
    first = tmp_path / "notepad.exe"
    first.write_bytes(b"safe executable fixture, never executed")
    renamed = tmp_path / "game.exe"
    renamed.write_bytes(first.read_bytes())
    hasher = ExecutableHasher()
    digest = hasher.digest(first)
    rules = AppRules("blocklist", [{"name": "notepad.exe", "sha256": digest}])
    assert rules.blocked(renamed.name, hasher.digest(renamed))
    allow = AppRules("allowlist", [{"name": "notepad.exe", "sha256": digest}])
    assert allow.blocked("notepad.exe", "0" * 64)


def test_app_hash_cache_invalidated(tmp_path):
    path = tmp_path / "test.exe"
    path.write_bytes(b"first")
    hasher = ExecutableHasher()
    first = hasher.digest(path)
    path.write_bytes(b"changed contents")
    assert hasher.digest(path) != first


def upstream(data, tcp=False):
    query = DNSRecord.parse(data)
    reply = query.reply()
    reply.add_answer(RR(query.q.qname, QTYPE.A, ttl=30, rdata=A("192.0.2.10")))
    return reply.pack()


def test_domain_boundaries_public_suffix_and_doh():
    assert matches("a.example.com", "example.com")
    assert not matches("notexample.com", "example.com")
    assert event_domain("portal.school.edu.vn") == "school.edu.vn"
    assert event_domain('child-laptop.local') == ''
    assert event_domain('_service._tcp.example.com') == 'example.com'
    resolver = Resolver(block_doh=True, upstream_query=upstream)
    assert DNSRecord.parse(resolver.resolve(DNSRecord.question("use-application-dns.net").pack())).header.rcode == RCODE.NXDOMAIN


def test_dns_private_names_not_logged_and_srv_subdomains_still_blocked():
    logged = []
    resolver = Resolver(['example.com'], upstream_query=upstream, on_query=lambda *args: logged.append(args))
    assert DNSRecord.parse(resolver.resolve(DNSRecord.question('child-laptop.local').pack())).header.rcode == RCODE.NOERROR
    assert logged == []
    assert DNSRecord.parse(resolver.resolve(DNSRecord.question('_service._tcp.example.com', 'SRV').pack())).header.rcode == RCODE.NXDOMAIN
    assert logged == [('example.com', True)]


def test_dns_safesearch_and_https_hints():
    resolver = Resolver(upstream_query=upstream)
    response = DNSRecord.parse(resolver.resolve(DNSRecord.question("www.google.com").pack()))
    assert str(response.rr[0].rdata) == "forcesafesearch.google.com."
    hints = DNSRecord.question("www.google.com", "HTTPS")
    assert not DNSRecord.parse(resolver.resolve(hints.pack())).rr


@pytest.mark.parametrize("tcp", [False, True])
def test_real_loopback_dns_udp_tcp(tcp):
    proxy = DNSProxy(Resolver(["example.com"], upstream_query=upstream), port=0).start()
    try:
        query = DNSRecord.question("a.example.com")
        answer = query.send("127.0.0.1", proxy.port, tcp=tcp, timeout=2)
        assert DNSRecord.parse(answer).header.rcode == RCODE.NXDOMAIN
        good = DNSRecord.question("example.org")
        answer = good.send("127.0.0.1", proxy.port, tcp=tcp, timeout=2)
        assert str(DNSRecord.parse(answer).rr[0].rdata) == "192.0.2.10"
    finally:
        proxy.stop()


def test_dns_rejects_mismatched_upstream():
    def bad(data, tcp):
        reply = DNSRecord.parse(upstream(data)).reply()
        reply.header.id += 1
        return reply.pack()
    resolver = Resolver(upstream_query=bad)
    assert DNSRecord.parse(resolver.resolve(DNSRecord.question("example.org").pack())).header.rcode == RCODE.SERVFAIL


def test_clock_sync_accepts_local_offset_without_repeated_false_lock(store, policy):
    enforcer, clock = engine(store, policy)
    clock.wall -= 10800
    assert step(enforcer, clock)['clock_suspect']
    enforcer.sync_time(enforcer.trusted)
    assert step(enforcer, clock)['reason'] is None


def test_late_add_time_is_once_even_after_newer_lock(store, policy):
    enforcer, clock = engine(store, policy)
    earlier = command(enforcer, 'add_time', 1, day=enforcer.current_day().date().isoformat())
    enforcer.command(command(enforcer, 'lock', 2))
    assert enforcer.command(earlier)
    assert enforcer.budget() == 1080
    assert enforcer.reason() == 'parent_lock'
    assert not enforcer.command(earlier)
    assert set(store.get('pending_acks')) == {'1', '2'}


def test_suspend_gap_never_charges_suspended_hour(store, policy):
    enforcer, clock = engine(store, policy)
    before = enforcer.trusted
    step(enforcer, clock, 3600)
    assert enforcer.usage() == (0, 0)
    assert enforcer.trusted == before + 3600


def test_future_allocation_reduction_keeps_today_budget(store, policy):
    enforcer, clock = engine(store, policy)
    enforcer.command(command(enforcer, 'reduce_budget', weekday_sec=30, weekend_sec=20, effective_date='2026-11-05'))
    assert enforcer.budget('2026-11-04') == 180
    assert enforcer.budget('2026-11-05') == 30


class FakeProcess:
    def __init__(self, pid, path):
        self.pid, self.path, self.terminated = pid, str(path), False
    def exe(self): return self.path
    def username(self): return 'LAB\\child'
    def name(self): return 'example.exe'
    def create_time(self): return 10
    def terminate(self): self.terminated = True


def test_app_monitor_foreground_durations_and_no_locked_time(tmp_path):
    path = tmp_path / 'example.exe'
    path.write_bytes(b'never executed')
    process = FakeProcess(321, path)
    clock, events = Clock(), []
    monitor = AppMonitor('LAB\\child', AppRules('blocklist', []), lambda *args: events.append(args), lambda name: True, processes=lambda: [process], monotonic=lambda: clock.mono)
    monitor.tick(321, active=True)
    clock.advance(2)
    monitor.tick(321, active=True)
    clock.advance(1)
    monitor.tick(0, active=False)
    assert events == [('app_start', 'example.exe', 0), ('app_stop', 'example.exe', 2)]


def test_app_monitor_explanation_ack_precedes_terminate(tmp_path):
    path = tmp_path / 'example.exe'
    path.write_bytes(b'never executed')
    process = FakeProcess(321, path)
    rules = AppRules('blocklist', [{'name': 'example.exe'}])
    assert not terminate_verified(process, path, 10, ExecutableHasher(), rules, lambda name: None)
    assert not process.terminated
    assert terminate_verified(process, path, 10, ExecutableHasher(), rules, lambda name: True)
    assert process.terminated


def test_process_pid_reuse_does_not_terminate(tmp_path):
    path = tmp_path / 'example.exe'
    path.write_bytes(b'never executed')
    process = FakeProcess(321, path)
    assert not terminate_verified(process, path, 9, ExecutableHasher(), AppRules('blocklist', [{'name': 'example.exe'}]), lambda name: True)
    assert not process.terminated


@pytest.mark.parametrize('trusted', [False, True])
def test_real_ipc_requires_verified_peer_even_with_correct_token(trusted):
    leases = []
    ipc = TrayIPC('x' * 40, lambda: {'reason': None}, lambda payload: leases.append(payload), lambda: None, port=0, verify_peer=(lambda payload, address: True) if trusted else None)
    ipc.start()
    connection = http.client.HTTPConnection('127.0.0.1', ipc.server.server_address[1], timeout=2)
    try:
        connection.request('POST', '/lease', json.dumps({'icon_visible': True, 'pid': 999}), {'Authorization': 'Bearer ' + 'x' * 40})
        response = connection.getresponse()
        response.read()
        assert response.status == (200 if trusted else 403)
        assert bool(leases) == trusted
    finally:
        connection.close()
        ipc.stop()


def test_real_ipc_rejects_browser_origin_and_wrong_token():
    ipc = TrayIPC('x' * 40, lambda: {}, lambda payload: None, lambda: None, port=0, verify_peer=lambda payload, address: True)
    ipc.start()
    try:
        for headers in ({'Authorization': 'Bearer bad'}, {'Authorization': 'Bearer ' + 'x' * 40, 'Origin': 'https://example.com'}):
            connection = http.client.HTTPConnection('127.0.0.1', ipc.server.server_address[1], timeout=2)
            connection.request('POST', '/lease', '{}', headers)
            response = connection.getresponse()
            response.read()
            assert response.status == 403
            connection.close()
    finally:
        ipc.stop()


def test_deletion_command_purges_usage_and_keeps_atomic_cleanup_ack(store, policy):
    enforcer, clock = engine(store, policy)
    step(enforcer, clock)
    store.queue(event())
    store.batch()
    enforcer.command(command(enforcer, 'delete_data', generation=9))
    assert not store.db.execute('SELECT * FROM usage').fetchall()
    assert store.batch() is None
    assert store.get('pending_acks') == ['1']
    assert store.get('deletion_generation') == 9
    assert enforcer.stopped


def test_real_ipv6_loopback_dns_tcp_udp():
    proxy = DNSProxy(Resolver(['example.com'], upstream_query=upstream), host='::1', port=0).start()
    try:
        data = DNSRecord.question('example.com').pack()
        for tcp in (False, True):
            with socket.socket(socket.AF_INET6, socket.SOCK_STREAM if tcp else socket.SOCK_DGRAM) as client:
                client.settimeout(2)
                client.connect(('::1', proxy.port))
                if tcp:
                    client.sendall(struct.pack('!H', len(data)) + data)
                    length = struct.unpack('!H', Resolver._read_exact(client, 2))[0]
                    answer = Resolver._read_exact(client, length)
                else:
                    client.send(data)
                    answer = client.recv(4096)
                assert DNSRecord.parse(answer).header.rcode == RCODE.NXDOMAIN
    finally:
        proxy.stop()


def test_deletion_tombstone_fences_late_worker_events(store):
    store.delete_child_data(12)
    assert store.queue(event()) is False
    assert store.batch() is None


def test_completed_deletion_never_reenrolls_on_service_restart(tmp_path):
    path = tmp_path / 'deleted.sqlite'
    cache = Store(path)
    cache.put('deletion_generation', 12)
    cache.put('credentials_dpapi', None)
    cache.close()
    config = tmp_path / 'config.json'
    config.write_text(json.dumps({'lab_enforcement': True, 'database': str(path)}))
    runtime = Runtime(config)
    assert runtime.cleanup_complete
    runtime.run()


def test_lost_deletion_ack_revoked_credentials_finish_cleanup(store):
    runtime = Runtime.__new__(Runtime)
    runtime.store = store
    store.put('pending_acks', ['delete1'])
    store.put('credentials_dpapi', 'encrypted-fixture')
    class RevokedSync:
        def call(self, *args): raise HTTPFailure(403)
    runtime.sync = RevokedSync()
    runtime.acknowledge_deletion('delete1')
    assert store.get('pending_acks') == []
    assert store.get('credentials_dpapi') is None


def test_app_explanation_pending_ack_and_timeout(monkeypatch):
    runtime = Runtime.__new__(Runtime)
    runtime.guard = threading.RLock()
    runtime.explanation = None
    runtime.explanation_ack = None
    assert runtime.explain('game.exe') is None
    identity = runtime.explanation['id']
    assert runtime.explain('different.exe') is None
    runtime.explanation_ack = identity
    assert runtime.explain('game.exe') is True
    assert runtime.explanation is None
    assert runtime.explain('game.exe') is None
    monkeypatch.setattr('agent.runtime.time.monotonic', lambda: runtime.explanation['deadline'] + 1)
    assert runtime.explain('game.exe') is False
