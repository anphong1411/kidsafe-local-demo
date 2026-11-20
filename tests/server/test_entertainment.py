from datetime import datetime, timezone
from zoneinfo import ZoneInfo

import pytest
from sqlalchemy import text

from test_backend import lab, child, enroll, auth
from server.app import create_app


def test_entertainment_policy_persists_and_signed_agent_policy_matches(lab):
    _, client = lab
    cid = child(client)
    route = f'/api/children/{cid}/policy'
    policy = client.get(route).json()['policy']
    original = policy['weekday_quota_sec'], policy['weekend_quota_sec']
    policy.update(entertainment_quota_sec=2700, entertainment_apps=['Game.exe', 'game.exe', 'video.exe'])
    policy.update(apps=[{'name': 'game.exe', 'sha256': '0' * 64}],
                  blocked_categories=[], blocked_domains=['Example.org', 'example.org'])
    assert client.put(route, json=policy).status_code == 200
    saved = client.get(route).json()
    assert saved['policy']['entertainment_quota_sec'] == 2700
    assert saved['policy']['entertainment_apps'] == ['game.exe', 'video.exe']
    assert (saved['policy']['weekday_quota_sec'], saved['policy']['weekend_quota_sec']) == original
    assert saved['stats']['controlled_app_count'] == 2
    assert saved['stats']['blocked_domain_count'] == 1
    device, _ = enroll(client, cid)
    signed = client.get('/api/device/policy', headers=auth(device)).json()['payload']
    assert signed['entertainment_quota_sec'] == 2700 and signed['entertainment_apps'] == ['game.exe', 'video.exe']
    changes = client.get(f'/api/children/{cid}/audit').json()
    edit = next(change for change in changes if change['action'] == 'update_policy')
    assert edit['new']['entertainment_quota_sec'] == 2700
    assert edit['new']['entertainment_apps'] == ['game.exe', 'video.exe']


@pytest.mark.parametrize('field,value', [('entertainment_quota_sec', -1), ('entertainment_quota_sec', 86401),
                                        ('weekday_quota_sec', 3599), ('weekend_quota_sec', 3599),
                                        ('entertainment_apps', ['C:/game.exe']), ('entertainment_apps', ['https://example.org'])])
def test_entertainment_rejects_bad_policy(lab, field, value):
    _, client = lab
    cid = child(client)
    route = f'/api/children/{cid}/policy'
    policy = client.get(route).json()['policy']
    policy[field] = value
    assert client.put(route, json=policy).status_code == 422


def test_entertainment_is_separate_monotonic_shared_and_not_reset_by_legacy_heartbeat(lab):
    _, client = lab
    cid = child(client)
    first, _ = enroll(client, cid)
    second, _ = enroll(client, cid)
    today = datetime.now(timezone.utc).astimezone(ZoneInfo('Asia/Ho_Chi_Minh')).date().isoformat()
    for device, normal, entertainment, peer in [(first, 600, 180, 0), (second, 300, 60, 180)]:
        body = {'device_id': device['device_id'], 'status': 'active', 'quota_used_sec': normal,
                'entertainment_used_sec': entertainment, 'policy_version': 1, 'usage_date': today}
        response = client.post('/api/device/heartbeat', json=body, headers=auth(device))
        assert response.status_code == 200 and response.json()['entertainment_other_sec'] == peer
    route = f'/api/children/{cid}/reports?days=1'
    report = client.get(route).json()
    assert report['total_seconds'] == 900
    assert report['entertainment_today'] == {'quota_sec': 3600, 'used_sec': 240, 'remaining_sec': 3360,
                                              'reporting_devices': 2, 'devices_count': 2}
    # A repeated or older heartbeat must not erase the independent counter.
    body = {'device_id': first['device_id'], 'status': 'active', 'quota_used_sec': 600,
            'policy_version': 1, 'usage_date': today, 'entertainment_used_sec': 60}
    assert client.post('/api/device/heartbeat', json=body, headers=auth(first)).json()['entertainment_other_sec'] == 60
    del body['entertainment_used_sec']
    client.post('/api/device/heartbeat', json=body, headers=auth(first)).raise_for_status()
    assert client.get(route).json()['entertainment_today']['used_sec'] == 240
    policy_route = f'/api/children/{cid}/policy'
    policy = client.get(policy_route).json()['policy']
    policy['entertainment_quota_sec'] = 120
    assert client.put(policy_route, json=policy).status_code == 200
    assert client.get(route).json()['entertainment_today']['remaining_sec'] == 0
    assert client.get(route).json()['entertainment_today']['used_sec'] == 240


def test_legacy_policy_and_agent_data_have_explicit_tracking_status(lab):
    app, client = lab
    cid = child(client)
    with app.state.database.session() as db:
        db.execute(text("UPDATE children SET policy=json_remove(policy,'$.entertainment_quota_sec','$.entertainment_apps') WHERE id=:id"), {'id': cid})
    policy = client.get(f'/api/children/{cid}/policy').json()['policy']
    assert policy['entertainment_quota_sec'] == 3600 and policy['entertainment_apps'] == []
    enroll(client, cid)
    report = client.get(f'/api/children/{cid}/reports').json()['entertainment_today']
    assert report['reporting_devices'] == 0 and report['devices_count'] == 1
    assert report['remaining_sec'] == 3600


def test_group_policy_signed_and_group_usage_is_monotonic_and_child_scoped(lab):
    _, client = lab
    cid = child(client)
    route = f'/api/children/{cid}/policy'
    policy = client.get(route).json()['policy']
    group = policy['app_groups']['video']
    group.update(mode='custom', quota_sec=900, apps=[{'name': 'video.EXE', 'sha256': 'a'*64}],
                 message='Con có thể đọc sách nhé.', window={'days': [0, 5], 'start_minute': 1080, 'end_minute': 1260})
    client.put(route, json=policy).raise_for_status()
    assert client.get(route).json()['stats']['controlled_app_count'] == 1
    # A legacy editor omitting the new field must preserve signed group configuration.
    legacy_policy = {key: value for key, value in policy.items() if key != 'app_groups'}
    client.put(route, json=legacy_policy).raise_for_status()
    first, _ = enroll(client, cid)
    second, _ = enroll(client, cid)
    outsider, _ = enroll(client, child(client))
    assert first['policy']['payload']['app_groups']['video'] == group
    today = datetime.now(ZoneInfo('Asia/Ho_Chi_Minh')).date().isoformat()

    def heartbeat(device, groups):
        body = {'device_id': device['device_id'], 'status': 'active', 'quota_used_sec': 300,
                'entertainment_used_sec': 0, 'policy_version': 1, 'usage_date': today}
        if groups is not None:
            body['group_used_sec'] = groups
        return client.post('/api/device/heartbeat', headers=auth(device), json=body)

    heartbeat(outsider, {'video': 800}).raise_for_status()
    heartbeat(first, {'video': 120}).raise_for_status()
    heartbeat(first, None).raise_for_status()
    assert heartbeat(second, {'video': 20}).json()['group_other_sec'] == {'video': 120}
    assert heartbeat(first, {'video': 10}).json()['group_other_sec'] == {'video': 20}
    report = client.get(f'/api/children/{cid}/reports?days=1').json()
    assert report['app_group_today_seconds'] == {'video': 140}
    assert report['entertainment_today']['used_sec'] == 0 and report['total_seconds'] == 600


@pytest.mark.parametrize('problem', ['duplicate_digest', 'overnight', 'unlocked_blocklist', 'missing_quota'])
def test_invalid_group_policy_is_rejected(lab, problem):
    _, client = lab
    route = f'/api/children/{child(client)}/policy'
    policy = client.get(route).json()['policy']
    groups = policy['app_groups']
    if problem == 'duplicate_digest':
        groups['games']['apps'] = [{'name': 'a.exe', 'sha256': 'a'*64}]
        groups['study']['apps'] = [{'name': 'b.exe', 'sha256': 'A'*64}]
    elif problem == 'overnight':
        groups['games']['window'] = {'days': [0], 'start_minute': 1320, 'end_minute': 60}
    elif problem == 'unlocked_blocklist':
        groups['blocked']['enabled'] = True
    else:
        groups['study']['mode'] = 'custom'
    assert client.put(route, json=policy).status_code == 422


@pytest.mark.parametrize('legacy_quota,daily_limit,expected', [(None, 7200, 3600), (3600, 1800, 1800)])
def test_upgrade_bumps_signed_policy_once_and_audits_the_system_change(lab, legacy_quota, daily_limit, expected):
    app, client = lab
    cid = child(client)
    version = client.get(f'/api/children/{cid}/policy').json()['version']
    with app.state.database.session() as db:
        if legacy_quota is None:
            db.execute(text("UPDATE children SET policy=json_remove(policy,'$.entertainment_quota_sec','$.entertainment_apps') WHERE id=:id"), {'id': cid})
        else:
            db.execute(text("UPDATE children SET policy=json_set(policy,'$.weekday_quota_sec',:day,'$.entertainment_quota_sec',:quota) WHERE id=:id"),
                       {'id': cid, 'day': daily_limit, 'quota': legacy_quota})
    upgraded = create_app(app.state.settings)
    try:
        policy = client.get(f'/api/children/{cid}/policy').json()
        assert policy['version'] == version + 1
        audit = next(a for a in client.get(f'/api/children/{cid}/audit').json() if a['action'] == 'upgrade_entertainment_policy')
        assert audit['actor'] == 'system' and audit['new']['entertainment_quota_sec'] == expected
        assert policy['policy']['weekday_quota_sec'] == daily_limit
        again = create_app(app.state.settings)
        again.state.database.engine.dispose()
        assert client.get(f'/api/children/{cid}/policy').json()['version'] == version + 1
    finally:
        upgraded.state.database.engine.dispose()
