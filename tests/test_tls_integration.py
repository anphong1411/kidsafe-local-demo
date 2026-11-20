"""Real sockets: HTTPS server -> pinned agent -> signed policy -> durable counter."""
import base64
from datetime import datetime, timezone
import secrets
import socket
import ssl
import threading
import time
from uuid import uuid4

import httpx
import pytest
import uvicorn

from agent.policy import verify_envelope
from agent.transport import PinnedHTTPS
from agent.storage import Store
from agent.sync import DeviceSync
from scripts.create_lab_tls import generate
from server.app import create_app
from server.config import Settings
from server.models import Account
from server.security import password_hash


@pytest.fixture
def live_server(tmp_path):
    pin = generate(tmp_path / 'tls', [])
    app = create_app(Settings('sqlite:///' + (tmp_path / 'test.db').as_posix(),
                              secrets.token_bytes(32), secrets.token_bytes(32)))
    password = secrets.token_urlsafe(18)
    with app.state.database.session() as db:
        db.add(Account(id=str(uuid4()), username='test-parent', password=password_hash(password), role='parent'))
    listener = socket.socket()
    listener.bind(('127.0.0.1', 0))
    port = listener.getsockname()[1]
    config = uvicorn.Config(app, log_level='error', access_log=False,
                            ssl_keyfile=str(tmp_path / 'tls/server.key'),
                            ssl_certfile=str(tmp_path / 'tls/server.crt'))
    server = uvicorn.Server(config)
    thread = threading.Thread(target=server.run, kwargs={'sockets': [listener]}, daemon=True)
    thread.start()
    try:
        deadline = time.monotonic() + 10
        while not server.started and thread.is_alive() and time.monotonic() < deadline:
            time.sleep(.05)
        assert server.started
        yield f'https://localhost:{port}', pin, tmp_path / 'tls/ca.crt', password
    finally:
        server.should_exit = True
        thread.join(timeout=10)
        listener.close()
        assert not thread.is_alive(), 'Test server did not stop'


def test_real_enrollment_policy_event_retry_and_command(live_server):
    origin, pin, ca, password = live_server
    client = PinnedHTTPS(origin, ca, pin)
    context = ssl.create_default_context(cafile=str(ca))
    with httpx.Client(base_url=origin, verify=context, trust_env=False) as parent:
        response = parent.post('/api/auth/login', json={'username': 'test-parent', 'password': password})
        assert response.status_code == 200, response.text
        parent.headers['X-CSRF-Token'] = response.json()['csrf_token']
        child_response = parent.post('/api/children', json={'name': 'Demo child'})
        assert child_response.status_code == 201, child_response.text
        child = child_response.json()['id']
        code = parent.post(f'/api/children/{child}/enroll-codes', json={'consent': True}).json()['code']
        enrollment = client.request('POST', '/api/device/enroll', {
            'code': code, 'fingerprint': 'safe-test-fingerprint-' + str(uuid4()), 'name': 'Loopback test'})
        device, access = enrollment['device_id'], enrollment['access_token']
        policy = verify_envelope(enrollment['policy'], enrollment['signing_public_key'], device)
        assert policy['device_id'] == device
        again = client.request('GET', '/api/device/policy', token=access)
        assert again['payload'] == enrollment['policy']['payload']
        event = {'ts': datetime.now(timezone.utc).isoformat(), 'device_id': device,
                 'child_id': child, 'type': 'domain_query', 'subject': 'example.org',
                 'duration_sec': 0, 'policy_id': str(policy.get('policy_id', policy['version']))}
        first = client.request('POST', '/api/device/events', {'events': [event]}, access,
                               {'Idempotency-Key': 'integration-event-001'})
        second = client.request('POST', '/api/device/events', {'events': [event]}, access,
                                {'Idempotency-Key': 'integration-event-001'})
        assert first['accepted'] == 1 and not first['duplicate']
        assert second['duplicate']
        command = parent.post(f'/api/children/{child}/commands',
                              json={'device_id': device, 'type': 'add_time'},
                              headers={'Idempotency-Key': 'integration-command-001'})
        assert command.status_code == 201, command.text
        heartbeat = client.request('POST', '/api/device/heartbeat', {
            'device_id': device, 'status': 'active', 'quota_used_sec': 0,
            'policy_version': policy['version'], 'usage_date': datetime.now(timezone.utc).date().isoformat()}, access)
        assert any(c['payload']['id'] == command.json()['payload']['id'] for c in heartbeat['commands'])
        result = client.request('POST', '/api/device/commands/' + command.json()['payload']['id'] + '/ack', token=access)
        assert result['ok']
        deleted = parent.delete(f'/api/children/{child}')
        assert deleted.status_code == 200
        cleanup = client.request('POST', '/api/device/heartbeat', {
            'device_id': device, 'status': 'active', 'quota_used_sec': 0,
            'policy_version': policy['version'], 'usage_date': datetime.now(timezone.utc).date().isoformat()}, access)
        deletion = next(c['payload'] for c in cleanup['commands'] if c['payload']['type'] == 'delete_data')
        path = '/api/device/commands/' + deletion['id'] + '/ack'
        assert client.request('POST', path, token=access)['ok']
        # Lost ACK response must be recoverable without restoring collection access.
        assert client.request('POST', path, token=access)['duplicate']
        from agent.transport import HTTPFailure
        with pytest.raises(HTTPFailure) as refused:
            client.request('POST', '/api/device/events', {'events': [event]}, access,
                           {'Idempotency-Key': 'after-delete-forbidden'})
        assert refused.value.status == 410


def test_pin_mismatch_refused_before_api(live_server):
    origin, _, ca, _ = live_server
    with pytest.raises(ssl.SSLError, match='pin mismatch'):
        PinnedHTTPS(origin, ca, '0' * 64).request('GET', '/api/device/policy', token='must-not-be-sent')


def test_real_pinned_websocket_urgent_command(live_server, tmp_path, record_property):
    origin, pin, ca, password = live_server
    transport = PinnedHTTPS(origin, ca, pin)
    store = Store(tmp_path / 'ws-agent.db')
    sync = None
    thread = None
    try:
        with httpx.Client(base_url=origin, verify=ssl.create_default_context(cafile=str(ca)), trust_env=False) as parent:
            login = parent.post('/api/auth/login', json={'username': 'test-parent', 'password': password})
            parent.headers['X-CSRF-Token'] = login.json()['csrf_token']
            child = parent.post('/api/children', json={'name': 'WebSocket test'}).json()['id']
            code = parent.post(f'/api/children/{child}/enroll-codes', json={'consent': True}).json()['code']
            enrollment = transport.request('POST', '/api/device/enroll', {
                'code': code, 'fingerprint': str(uuid4()), 'name': 'WS loopback'})
            credentials = {k: enrollment[k] for k in ('device_id', 'child_id', 'access_token', 'refresh_token')}
            sync = DeviceSync(store, transport, credentials, enrollment['signing_public_key'])
            thread = threading.Thread(target=sync.websocket, daemon=True)
            thread.start()
            assert sync.incoming.get(timeout=8)[0] == 'time'
            sent = time.monotonic()
            command = parent.post(f'/api/children/{child}/commands',
                json={'device_id': credentials['device_id'], 'type': 'lock'},
                headers={'Idempotency-Key': str(uuid4())})
            assert command.status_code == 201
            kind, payload = sync.incoming.get(timeout=4)
            latency = time.monotonic() - sent
            assert kind == 'command' and payload['id'] == command.json()['payload']['id']
            assert latency < 5
            record_property('api_to_verified_agent_queue_seconds', latency)
            record_property('scope', 'Localhost protocol only; not Windows lock latency')
    finally:
        if sync:
            sync.stop_event.set()
        if thread:
            thread.join(timeout=7)
            assert not thread.is_alive()
        store.close()
