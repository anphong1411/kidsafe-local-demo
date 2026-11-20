import base64
import json
from datetime import datetime, timezone, timedelta
from concurrent.futures import ThreadPoolExecutor
from uuid import uuid4

import pytest
from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
from fastapi.testclient import TestClient
from sqlalchemy import select, text

from server.app import create_app, now, stamp
from server.config import Settings
from server.models import Account, Audit, Child, Command, Device, DeviceToken, Session
from server.schemas import EventInput, PolicyInput
from server.security import Crypto, canonical, digest, password_hash, password_verify


@pytest.fixture
def lab(tmp_path):
    app = create_app(Settings(f"sqlite:///{tmp_path / 'test.db'}", b'a' * 32, b'b' * 32))
    with app.state.database.session() as db:
        db.add_all([Account(id='parent1', username='parent1', password=password_hash('correct-pass1'), role='parent'),
                    Account(id='parent2', username='parent2', password=password_hash('correct-pass2'), role='parent')])
    with TestClient(app, base_url='https://testserver') as client:
        login = client.post('/api/auth/login', json={'username': 'parent1', 'password': 'correct-pass1'})
        client.headers['X-CSRF-Token'] = login.json()['csrf_token']
        yield app, client


def child(client):
    response = client.post('/api/children', json={'name': 'An'})
    assert response.status_code == 201, response.text
    return response.json()['id']


def enroll(client, child_id, fingerprint=None):
    code = client.post(f'/api/children/{child_id}/enroll-codes', json={'consent': True}).json()['code']
    result = client.post('/api/device/enroll', json={'code': code, 'fingerprint': fingerprint or uuid4().hex, 'name': 'Laptop'})
    assert result.status_code == 201, result.text
    return result.json(), code


def auth(device):
    return {'Authorization': 'Bearer ' + device['access_token']}


def event(device, **changes):
    return {'ts': stamp(), 'device_id': device['device_id'], 'child_id': device['child_id'],
            'type': 'domain_query', 'subject': 'example.com', 'duration_sec': 0,
            'policy_id': device['policy']['payload']['policy_id'], **changes}


def test_password_scrypt_and_minimum():
    hashed = password_hash('1234567890')
    assert hashed.startswith('scrypt$') and password_verify('1234567890', hashed)
    assert not password_verify('incorrect', hashed)
    with pytest.raises(ValueError):
        password_hash('short')


def test_aes_nonce_and_signature_integrity():
    crypto = Crypto(b'a' * 32, b'b' * 32)
    one, two = crypto.encrypt('private'), crypto.encrypt('private')
    assert one != two and crypto.decrypt(one) == 'private'
    envelope = crypto.envelope({'version': 1})
    public = Ed25519PublicKey.from_public_bytes(base64.b64decode(envelope['public_key']))
    public.verify(base64.b64decode(envelope['signature']), canonical(envelope['payload']))
    with pytest.raises(InvalidSignature):
        public.verify(base64.b64decode(envelope['signature']), canonical({'version': 2}))


def test_schedule_and_event_schema_negative():
    with pytest.raises(ValueError):
        PolicyInput(schedule=[[True] * 48] * 6)
    with pytest.raises(ValueError):
        EventInput(ts=stamp(), device_id='d', child_id='c', type='screen_capture', subject='', duration_sec=0, policy_id='p')
    with pytest.raises(ValueError):
        EventInput(ts=stamp(), device_id='d', child_id='c', type='domain_query', subject='https://example.com/chat?q=secret', duration_sec=0, policy_id='p')


def test_cookie_flags_csrf_and_logout(lab):
    app, client = lab
    result = client.post('/api/auth/login', json={'username': 'parent1', 'password': 'correct-pass1'})
    cookie = result.headers['set-cookie']
    assert 'HttpOnly' in cookie and 'Secure' in cookie and 'SameSite=lax' in cookie and 'Max-Age=43200' in cookie
    client.headers.pop('X-CSRF-Token')
    assert client.post('/api/children', json={'name': 'An'}).status_code == 403
    client.headers['X-CSRF-Token'] = result.json()['csrf_token']
    assert client.post('/api/auth/logout').status_code == 200
    assert client.get('/api/children').status_code == 401


def test_five_failed_passwords_lock_account(lab):
    _, client = lab
    for _ in range(5):
        assert client.post('/api/auth/login', json={'username': 'parent2', 'password': 'wrong'}).status_code == 401
    assert client.post('/api/auth/login', json={'username': 'parent2', 'password': 'correct-pass2'}).status_code == 423


def test_ownership_and_encrypted_names(lab):
    app, client = lab
    child_id = child(client)
    with app.state.database.session() as db:
        record = db.get(Child, child_id)
        assert record.name_enc != 'An' and app.state.crypto.decrypt(record.name_enc) == 'An'
    result = client.post('/api/auth/login', json={'username': 'parent2', 'password': 'correct-pass2'})
    client.headers['X-CSRF-Token'] = result.json()['csrf_token']
    assert client.get(f'/api/children/{child_id}/policy').status_code == 404
    assert client.get(f'/api/children/{child_id}/reports').status_code == 404
    assert client.get('/api/children').json() == []


def test_child_view_read_only_audit(lab):
    app, client = lab
    child_id = child(client)
    with app.state.database.session() as db:
        db.add(Account(id='child', username='child', password=password_hash('child-password'), role='child-view', child_id=child_id))
    result = client.post('/api/auth/login', json={'username': 'child', 'password': 'child-password'})
    client.headers['X-CSRF-Token'] = result.json()['csrf_token']
    assert client.get(f'/api/children/{child_id}/audit').status_code == 200
    assert client.post('/api/children', json={'name': 'No'}).status_code == 403
    assert client.delete(f'/api/children/{child_id}').status_code == 403


def test_enrollment_one_use_tokens_binding_and_rotation(lab):
    app, client = lab
    child_id = child(client)
    device, code = enroll(client, child_id)
    assert len(code) == 8
    assert client.post('/api/device/enroll', json={'code': code, 'fingerprint': uuid4().hex, 'name': 'Again'}).status_code == 400
    assert client.post('/api/device/refresh', json={'device_id': 'other-device', 'refresh_token': device['refresh_token']}).status_code == 401
    result = client.post('/api/device/refresh', json={'device_id': device['device_id'], 'refresh_token': device['refresh_token']})
    assert result.status_code == 200
    assert client.get('/api/device/policy', headers=auth(device)).status_code == 401
    assert client.post('/api/device/refresh', json={'device_id': device['device_id'], 'refresh_token': device['refresh_token']}).status_code == 401


def test_signed_policy_stable_and_initial_budget_not_multiplied(lab):
    _, client = lab
    child_id = child(client)
    first, _ = enroll(client, child_id)
    second, _ = enroll(client, child_id)
    policy = client.get('/api/device/policy', headers=auth(first)).json()
    assert policy == first['policy']
    assert first['policy']['payload']['allocation']['weekday_sec'] == 7200
    assert second['policy']['payload']['allocation']['weekday_sec'] == 0
    assert policy['payload']['offline_after_days'] == 3


def test_event_idempotency_and_payload_multiplicity(lab):
    app, client = lab
    device, _ = enroll(client, child(client))
    payload = {'events': [event(device)] * 2}
    headers = {**auth(device), 'Idempotency-Key': 'batch-key-1'}
    assert client.post('/api/device/events', json=payload, headers=headers).json()['duplicate'] is False
    assert client.post('/api/device/events', json=payload, headers=headers).json()['duplicate'] is True
    changed = {'events': [event(device, subject='example.org')]}
    assert client.post('/api/device/events', json=changed, headers=headers).status_code == 409
    with app.state.database.session() as db:
        assert db.scalar(text('SELECT COUNT(*) FROM events')) == 2
        assert len(db.execute(text('PRAGMA table_info(events)')).all()) == 7


@pytest.mark.parametrize('changes', [{'child_id': 'other'}, {'device_id': 'other'}])
def test_event_cross_family_binding(lab, changes):
    _, client = lab
    device, _ = enroll(client, child(client))
    result = client.post('/api/device/events', json={'events': [event(device, **changes)]}, headers={**auth(device), 'Idempotency-Key': 'binding-key'})
    assert result.status_code == 403


@pytest.mark.parametrize('subject', ['www.example.com', 'https://example.com/path', 'example.com/private', 'sub.school.edu.vn'])
def test_domain_subject_minimization(lab, subject):
    _, client = lab
    device, _ = enroll(client, child(client))
    assert client.post('/api/device/events', json={'events': [event(device, subject=subject)]}, headers={**auth(device), 'Idempotency-Key': uuid4().hex}).status_code == 422


def test_command_idempotency_sequence_and_d017(lab):
    app, client = lab
    child_id = child(client)
    device, _ = enroll(client, child_id)
    route = f'/api/children/{child_id}/commands'
    for key, kind in [('add-key-111', 'add_time'), ('unlock-key-1', 'unlock'), ('lock-key-111', 'lock')]:
        first = client.post(route, json={'device_id': device['device_id'], 'type': kind}, headers={'Idempotency-Key': key})
        second = client.post(route, json={'device_id': device['device_id'], 'type': kind}, headers={'Idempotency-Key': key})
        assert first.status_code == 201, first.text
        assert first.json() == second.json()
        if kind == 'add_time':
            assert first.json()['payload']['seconds'] == 900 and 'day' in first.json()['payload']
    with app.state.database.session() as db:
        commands = db.scalars(select(Command).order_by(Command.created, Command.id)).all()
        assert len(commands) == 3
        assert sorted(json.loads(row.payload)['sequence'] for row in commands) == [1, 2, 3]


def test_budget_transfer_waits_for_durable_ack_and_is_effective_tomorrow(lab):
    app, client = lab
    child_id = child(client)
    donor, _ = enroll(client, child_id)
    recipient, _ = enroll(client, child_id)
    result = client.post(f'/api/children/{child_id}/budget-transfers', json={'donor_id': donor['device_id'], 'recipient_id': recipient['device_id'], 'weekday_sec': 1800, 'weekend_sec': 1800})
    assert result.status_code == 201, result.text
    command = result.json()['command']['payload']
    assert command['effective_date'] > datetime.now().date().isoformat()
    assert client.get('/api/device/policy', headers=auth(recipient)).json()['payload']['allocation']['weekday_sec'] == 0
    ack_route = f"/api/device/commands/{command['id']}/ack"
    assert client.post(ack_route, json={}, headers=auth(donor)).status_code == 200
    assert client.post(ack_route, json={}, headers=auth(donor)).json()['duplicate']
    after = client.get('/api/device/policy', headers=auth(recipient)).json()['payload']['allocation']
    assert after['weekday_sec'] == 1800 and after['previous_weekday_sec'] == 0
    with app.state.database.session() as db:
        assert sum(d.weekday_sec for d in db.scalars(select(Device))) == 7200


def test_cannot_reduce_reserved_quota(lab):
    _, client = lab
    child_id = child(client)
    enroll(client, child_id)
    policy = PolicyInput(weekday_quota_sec=180, weekend_quota_sec=180).model_dump()
    assert client.put(f'/api/children/{child_id}/policy', json=policy).status_code == 409


def test_deletion_blocks_old_upload_and_supports_offline_cleanup(lab):
    app, client = lab
    child_id = child(client)
    device, _ = enroll(client, child_id)
    result = client.delete(f'/api/children/{child_id}')
    assert result.status_code == 200
    assert result.json()['pending_devices'] == [device['device_id']]
    assert client.post('/api/device/events', json={'events': [event(device)]}, headers={**auth(device), 'Idempotency-Key': 'deleted-batch'}).status_code == 410
    heartbeat = {'device_id': device['device_id'], 'status': 'locked', 'quota_used_sec': 0, 'policy_version': 1, 'usage_date': datetime.now().date().isoformat()}
    pending = client.post('/api/device/heartbeat', json=heartbeat, headers=auth(device)).json()['commands']
    assert len(pending) == 1 and pending[0]['payload']['type'] == 'delete_data'
    assert client.post(f"/api/device/commands/{pending[0]['payload']['id']}/ack", json={}, headers=auth(device)).status_code == 200
    assert client.get('/api/device/policy', headers=auth(device)).status_code == 401


def test_revocation_cleanup_only_and_then_child_deletion(lab):
    _, client = lab
    child_id = child(client)
    device, _ = enroll(client, child_id)
    assert client.delete(f"/api/children/{child_id}/devices/{device['device_id']}").status_code == 200
    assert client.get('/api/device/policy', headers=auth(device)).status_code == 401
    refreshed = client.post('/api/device/refresh', json={'device_id': device['device_id'], 'refresh_token': device['refresh_token']})
    assert refreshed.status_code == 200
    assert client.delete(f'/api/children/{child_id}').status_code == 200


def test_retention_removes_old_records(lab):
    app, client = lab
    with app.state.database.session() as db:
        db.execute(text("INSERT INTO events VALUES(:ts,'d','c','locked','',0,'p')"), {'ts': stamp(now() - 91 * 86400)})
    app.state.retention()
    with app.state.database.session() as db:
        assert db.scalar(text('SELECT COUNT(*) FROM events')) == 0


def test_report_heartbeat_monotonic_no_duplicate_duration(lab):
    _, client = lab
    child_id = child(client)
    device, _ = enroll(client, child_id)
    heartbeat = {'device_id': device['device_id'], 'status': 'active', 'quota_used_sec': 60, 'exception_used_sec': 10, 'policy_version': 1, 'usage_date': datetime.now().date().isoformat()}
    for used in [60, 60, 30]:
        heartbeat['quota_used_sec'] = used
        assert client.post('/api/device/heartbeat', json=heartbeat, headers=auth(device)).status_code == 200
    report = client.get(f'/api/children/{child_id}/reports').json()
    assert report['total_seconds'] == 70


def test_cross_origin_csrf_rejected(lab):
    _, client = lab
    assert client.post('/api/children', json={'name': 'bad'}, headers={'Origin': 'https://evil.example'}).status_code == 403


def test_parallel_same_command_serialized(lab):
    app, client = lab
    child_id = child(client)
    device, _ = enroll(client, child_id)
    def send(_):
        return client.post(f'/api/children/{child_id}/commands', json={'device_id': device['device_id'], 'type': 'add_time'}, headers={'Idempotency-Key': 'parallel-key'}).json()
    with ThreadPoolExecutor(max_workers=4) as executor:
        results = list(executor.map(send, range(4)))
    assert len({value['payload']['id'] for value in results}) == 1
    with app.state.database.session() as db:
        assert db.get(Device, device['device_id']).sequence == 1


def test_scoped_child_account_and_web_request_retry(lab):
    app, client = lab
    child_id = child(client)
    device, _ = enroll(client, child_id)
    result = client.post(f'/api/children/{child_id}/account', json={'username': 'child-login', 'password': 'child-password'})
    assert result.status_code == 201
    assert client.post(f'/api/children/{child_id}/requests', json={'device_id': device['device_id']}, headers={'Idempotency-Key': 'request-key'}).status_code == 403
    result = client.post('/api/auth/login', json={'username': 'child-login', 'password': 'child-password'})
    client.headers['X-CSRF-Token'] = result.json()['csrf_token']
    for duplicate in (False, True):
        result = client.post(f'/api/children/{child_id}/requests', json={'device_id': device['device_id']}, headers={'Idempotency-Key': 'request-key'})
        assert result.status_code == 201 and result.json()['duplicate'] is duplicate
    assert len(client.get(f'/api/children/{child_id}/reports').json()['requests']) == 1


def test_csrf_recovery_and_encrypted_audit(lab):
    app, client = lab
    client.headers['X-CSRF-Token'] = client.get('/api/auth/csrf').json()['csrf_token']
    child_id = child(client)
    assert client.get(f'/api/children/{child_id}/audit').json()[0]['action'] == 'create_child'
    with app.state.database.session() as db:
        row = db.scalar(select(Audit).where(Audit.child_id == child_id))
        assert row.ip != 'testclient' and not row.new.startswith('{')
        assert json.loads(app.state.crypto.decrypt(row.new))['id'] == child_id


def test_return_budget_requires_ack_and_preserves_today_reservation(lab):
    app, client = lab
    child_id = child(client)
    donor, _ = enroll(client, child_id)
    recipient, _ = enroll(client, child_id)
    result = client.put(f'/api/children/{child_id}/allocation', json={'device_id': donor['device_id'], 'weekday_sec': 1800, 'weekend_sec': 1800})
    assert result.status_code == 200, result.text
    command_id = result.json()['command']['payload']['id']
    assert client.post(f'/api/device/commands/{command_id}/ack', json={}, headers=auth(donor)).status_code == 200
    # The donor could already have spent its original allocation today. Do not reclaim it today.
    result = client.put(f'/api/children/{child_id}/allocation', json={'device_id': recipient['device_id'], 'weekday_sec': 5400, 'weekend_sec': 5400})
    assert result.status_code == 409
    assert client.put(f'/api/children/{child_id}/policy', json=PolicyInput(weekday_quota_sec=1800, weekend_quota_sec=1800).model_dump()).status_code == 409


def test_transfer_overlapping_pending_roles_rejected(lab):
    _, client = lab
    child_id = child(client)
    first, _ = enroll(client, child_id)
    second, _ = enroll(client, child_id)
    third, _ = enroll(client, child_id)
    result = client.post(f'/api/children/{child_id}/budget-transfers', json={'donor_id': first['device_id'], 'recipient_id': second['device_id'], 'weekday_sec': 100, 'weekend_sec': 100})
    assert result.status_code == 201
    result = client.post(f'/api/children/{child_id}/budget-transfers', json={'donor_id': first['device_id'], 'recipient_id': third['device_id'], 'weekday_sec': 100, 'weekend_sec': 100})
    assert result.status_code == 409


def test_reported_policy_status_and_command_ack_listing(lab):
    _, client = lab
    child_id = child(client)
    device, _ = enroll(client, child_id)
    heartbeat = {'device_id': device['device_id'], 'status': 'locked', 'quota_used_sec': 0, 'policy_version': 1, 'usage_date': datetime.now().date().isoformat()}
    assert client.post('/api/device/heartbeat', json=heartbeat, headers=auth(device)).status_code == 200
    result = client.get(f'/api/children/{child_id}/devices').json()[0]
    assert result['reported_policy_version'] == 1 and result['status'] == 'locked'
    command = client.post(f'/api/children/{child_id}/commands', json={'device_id': device['device_id'], 'type': 'lock'}, headers={'Idempotency-Key': 'show-ack-key'}).json()['payload']
    assert client.get(f'/api/children/{child_id}/commands').json()[0]['ack'] is False
    assert client.post(f"/api/device/commands/{command['id']}/ack", json={}, headers=auth(device)).status_code == 200
    assert client.get(f'/api/children/{child_id}/commands').json()[0]['ack'] is True


def test_deletion_status_and_ack_response_retry(lab):
    _, client = lab
    child_id = child(client)
    device, _ = enroll(client, child_id)
    assert client.delete(f'/api/children/{child_id}').status_code == 200
    assert not client.get(f'/api/children/{child_id}/deletion-status').json()['complete']
    heartbeat = {'device_id': device['device_id'], 'status': 'locked', 'quota_used_sec': 0, 'policy_version': 1, 'usage_date': datetime.now().date().isoformat()}
    command = client.post('/api/device/heartbeat', json=heartbeat, headers=auth(device)).json()['commands'][0]['payload']
    route = f"/api/device/commands/{command['id']}/ack"
    assert client.post(route, json={}, headers=auth(device)).status_code == 200
    assert client.post(route, json={}, headers=auth(device)).json()['duplicate']
    assert client.get(f'/api/children/{child_id}/deletion-status').json()['complete']


def test_exception_is_child_wide_not_multiplied_per_device(lab):
    _, client = lab
    child_id = child(client)
    first, _ = enroll(client, child_id)
    second, _ = enroll(client, child_id)
    route = f'/api/children/{child_id}/commands'
    assert client.post(route, json={'device_id': first['device_id'], 'type': 'unlock'}, headers={'Idempotency-Key': 'override-one'}).status_code == 201
    assert client.post(route, json={'device_id': second['device_id'], 'type': 'unlock'}, headers={'Idempotency-Key': 'override-two'}).status_code == 409
    lock = client.post(route, json={'device_id': first['device_id'], 'type': 'lock'}, headers={'Idempotency-Key': 'cancel-one'})
    assert lock.status_code == 201
    assert client.post(route, json={'device_id': second['device_id'], 'type': 'unlock'}, headers={'Idempotency-Key': 'still-pending'}).status_code == 409
    assert client.post(f"/api/device/commands/{lock.json()['payload']['id']}/ack", json={}, headers=auth(first)).status_code == 200
    assert client.post(route, json={'device_id': second['device_id'], 'type': 'unlock'}, headers={'Idempotency-Key': 'override-three'}).status_code == 201


@pytest.mark.parametrize('view', ['overview', 'time', 'apps', 'web', 'requests', 'devices', 'quick-control', 'reports', 'privacy'])
def test_parent_html_views_authorized_escaped_and_idor_safe(lab, view):
    _, client = lab
    name = '<img src=x onerror=alert(1)>'
    child_id = client.post('/api/children', json={'name': name}).json()['id']
    response = client.get(f'/app/{view}?child={child_id}')
    assert response.status_code == 200
    assert name not in response.text and '&lt;img' in response.text
    assert "script-src 'self'" in response.headers['content-security-policy']
    assert client.get(f'/app/{view}?child=someone-else').status_code == 404


def test_html_auth_redirects_and_child_scoping(lab):
    _, client = lab
    child_id = child(client)
    assert client.post(f'/api/children/{child_id}/account', json={'username': 'child-html', 'password': 'child-password'}).status_code == 201
    result = client.post('/api/auth/login', json={'username': 'child-html', 'password': 'child-password'})
    client.headers['X-CSRF-Token'] = result.json()['csrf_token']
    assert client.get('/app/overview', follow_redirects=False).headers['location'] == '/child'
    assert client.get('/child').status_code == 200
    assert client.get('/child?child=someone-else').status_code == 404
    assert client.get('/app/unknown').status_code == 404
    assert client.post('/api/auth/logout').status_code == 200
    for route in ('/app/overview', '/child'):
        result = client.get(route, follow_redirects=False)
        assert result.status_code == 303 and result.headers['location'] == '/login'


def test_report_normal_and_exception_funds_are_separate(lab):
    _, client = lab
    child_id = child(client)
    device, _ = enroll(client, child_id)
    command = client.post(f'/api/children/{child_id}/commands', json={'device_id': device['device_id'], 'type': 'add_time'}, headers={'Idempotency-Key': 'report-extra'})
    assert command.status_code == 201
    before = client.get(f'/api/children/{child_id}/reports?days=1').json()
    assert before['extra_granted_seconds'] == 0 and before['pending_extra_seconds'] == 900
    assert client.post(f"/api/device/commands/{command.json()['payload']['id']}/ack", json={}, headers=auth(device)).status_code == 200
    heartbeat = {'device_id': device['device_id'], 'status': 'active', 'quota_used_sec': 120, 'exception_used_sec': 30, 'policy_version': 1, 'usage_date': datetime.now().date().isoformat()}
    assert client.post('/api/device/heartbeat', json=heartbeat, headers=auth(device)).status_code == 200
    report = client.get(f'/api/children/{child_id}/reports?days=1').json()
    assert report['total_seconds'] == 150 and report['normal_seconds'] == 120 and report['extra_granted_seconds'] == 900


def test_pending_requests_remain_visible_and_distinguish_delivery_from_ack(lab):
    _, client = lab
    child_id = child(client)
    device, _ = enroll(client, child_id)
    recent = event(device, type='unlock_request', subject='more_time')
    old = {**recent, 'ts': (datetime.now(timezone.utc) - timedelta(days=8)).isoformat()}
    assert client.post('/api/device/events', json={'events': [old, recent]},
                       headers={**auth(device), 'Idempotency-Key': 'request-report-batch'}).status_code == 200
    route = f'/api/children/{child_id}'
    report = client.get(route + '/reports?days=7').json()
    assert len(report['requests']) == 1
    assert report['pending_request_count'] == 2
    assert {r['ts'] for r in report['pending_requests']} == {old['ts'], recent['ts']}

    key = f"request-{device['device_id']}-{recent['ts']}"
    approval = client.post(route + '/commands', json={'device_id': device['device_id'], 'type': 'add_time'},
                           headers={'Idempotency-Key': key})
    assert approval.status_code == 201
    report = client.get(route + '/reports').json()
    assert report['pending_request_count'] == 1
    assert report['pending_requests'][0]['ts'] == old['ts']
    assert report['requests'][0]['status'] == 'sent'
    assert report['extra_granted_seconds'] == 0

    command_id = approval.json()['payload']['id']
    assert client.post(f'/api/device/commands/{command_id}/ack', json={}, headers=auth(device)).status_code == 200
    report = client.get(route + '/reports').json()
    assert report['requests'][0]['status'] == 'acknowledged'
    assert report['extra_granted_seconds'] == 900
    # Repeating the same approval does not create a second grant.
    repeat = client.post(route + '/commands', json={'device_id': device['device_id'], 'type': 'add_time'},
                         headers={'Idempotency-Key': key})
    assert repeat.json()['payload']['id'] == command_id
    assert client.get(route + '/reports').json()['extra_granted_seconds'] == 900


def test_quick_time_grant_does_not_approve_unrelated_child_request(lab):
    _, client = lab
    child_id = child(client)
    device, _ = enroll(client, child_id)
    request = event(device, type='unlock_request', subject='more_time')
    assert client.post('/api/device/events', json={'events': [request]},
                       headers={**auth(device), 'Idempotency-Key': 'unrelated-request'}).status_code == 200
    response = client.post(f'/api/children/{child_id}/commands',
                           json={'device_id': device['device_id'], 'type': 'add_time'},
                           headers={'Idempotency-Key': 'quick-action-unrelated'})
    assert response.status_code == 201
    report = client.get(f'/api/children/{child_id}/reports').json()
    assert report['pending_request_count'] == 1
    assert report['requests'][0]['status'] == 'pending'


def test_long_offline_expired_refresh_is_cleanup_only(lab):
    app, client = lab
    child_id = child(client)
    device, _ = enroll(client, child_id)
    with app.state.database.session() as db:
        db.get(DeviceToken, digest(device['refresh_token'])).expires = now() - 86400
    app.state.retention()
    request = {'device_id': device['device_id'], 'refresh_token': device['refresh_token']}
    assert client.post('/api/device/refresh', json=request).status_code == 401
    assert client.delete(f'/api/children/{child_id}').status_code == 200
    cleanup_token = client.post('/api/device/refresh', json=request)
    assert cleanup_token.status_code == 200
    assert client.get('/api/device/policy', headers=auth(cleanup_token.json())).status_code == 401
    heartbeat = {'device_id': device['device_id'], 'status': 'locked', 'quota_used_sec': 0, 'policy_version': 1, 'usage_date': datetime.now().date().isoformat()}
    pending = client.post('/api/device/heartbeat', json=heartbeat, headers=auth(cleanup_token.json()))
    assert pending.status_code == 200 and pending.json()['commands'][0]['payload']['type'] == 'delete_data'


def test_auth_ip_rate_limit_bounds_even_invalid_schema(lab):
    _, client = lab
    responses = [client.post('/api/auth/login', json={}) for _ in range(31)]
    assert any(response.status_code == 422 for response in responses)
    assert responses[-1].status_code == 429 and responses[-1].headers['retry-after'] == '60'
