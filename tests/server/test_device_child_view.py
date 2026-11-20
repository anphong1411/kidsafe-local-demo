from fastapi.testclient import TestClient
from sqlalchemy import select

from server.models import Device
from test_backend import lab, child, enroll, auth, event


def test_paired_device_reads_only_its_child_without_web_account(lab):
    app, parent = lab
    first = child(parent)
    second = parent.post('/api/children', json={'name': 'Other child'}).json()['id']
    device, _ = enroll(parent, first)
    other, _ = enroll(parent, second)
    payload = event(device, type='app_stop', subject='notepad.exe', duration_sec=120)
    assert parent.post('/api/device/events', json={'events': [payload]}, headers={**auth(device), 'Idempotency-Key':'native-view-events'}).status_code == 200
    with TestClient(app, base_url='https://testserver') as anonymous:
        assert anonymous.get('/api/device/child-view').status_code == 401
        result = anonymous.get('/api/device/child-view?child_id='+second, headers=auth(device))
        assert result.status_code == 200
        data = result.json()
        assert data['name'] == 'An'
        assert data['top_apps'] == [{'subject':'notepad.exe','value':120}]
        assert all(set(item) == {'ts','icon','message'} for item in data['audit'])
        assert not any(key in data for key in ['password','token','child_id','device_id','policy','old','new'])
        assert anonymous.get('/api/device/child-view', headers=auth(other)).json()['top_apps'] == []
        with app.state.database.session() as db:
            db.get(Device, device['device_id']).revoked = True
        assert anonymous.get('/api/device/child-view', headers=auth(device)).status_code == 401


def test_native_requested_minutes_reach_parent_and_ack_returns_to_app(lab):
    _, parent = lab
    child_id = child(parent)
    device, _ = enroll(parent, child_id)
    requested = event(device, type='unlock_request', subject='more_time', duration_sec=300)
    headers = {**auth(device), 'Idempotency-Key':'native-more-time-batch'}
    assert parent.post('/api/device/events', json={'events':[requested]}, headers=headers).status_code == 200
    view = parent.get('/api/device/child-view', headers=auth(device)).json()
    assert view['last_request']['requested_minutes'] == 5 and view['last_request']['status'] == 'pending'
    key = f"request-{device['device_id']}-{requested['ts']}"
    command = parent.post(f'/api/children/{child_id}/commands', json={'device_id':device['device_id'],'type':'add_time'}, headers={'Idempotency-Key':key})
    assert command.status_code == 201 and command.json()['payload']['seconds'] == 300
    command_id = command.json()['payload']['id']
    assert parent.post(f'/api/device/commands/{command_id}/ack',json={},headers=auth(device)).status_code == 200
    assert parent.get('/api/device/child-view',headers=auth(device)).json()['last_request']['status'] == 'acknowledged'

