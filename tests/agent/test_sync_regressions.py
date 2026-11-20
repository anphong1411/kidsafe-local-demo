from agent.storage import Store
from agent.sync import DeviceSync


def test_deletion_heartbeat_does_not_fetch_policy_or_upload_old_events(tmp_path):
    calls = []

    class Transport:
        def request(self, method, path, body=None, token=None, headers=None):
            calls.append(path)
            if path == '/api/device/heartbeat':
                return {'deletion_pending': True, 'policy_version': 2, 'commands': []}
            raise AssertionError('Deletion must suppress policy fetch and uploads')

    store = Store(tmp_path / 'device.db')
    try:
        store.queue({'ts': '2026-11-04T00:00:00Z', 'device_id': 'd', 'child_id': 'c',
                     'type': 'domain_query', 'subject': 'example.org', 'duration_sec': 0, 'policy_id': '1'})
        sync = DeviceSync(store, Transport(), {'access_token': 'test', 'device_id': 'd'}, 'unused')
        sync.heartbeat({'policy_version': 1})
        assert calls == ['/api/device/heartbeat']
    finally:
        store.close()
