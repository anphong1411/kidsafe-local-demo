import http.client
import json
import threading
from types import SimpleNamespace

import pytest

from agent.child_window import presentation, minutes
from agent.entertainment import EntertainmentCounter
from agent.ipc import TrayIPC
from agent.runtime import Runtime
from agent.storage import QueueFull
from test_agent import store, policy, engine


def runtime(store, policy):
    result = Runtime.__new__(Runtime)
    result.store, result.policy, result.guard = store, policy, threading.RLock()
    result.engine, clock = engine(store, policy)
    result.entertainment = EntertainmentCounter(store)
    result.sync = SimpleNamespace(credentials={'device_id':'d1','child_id':'c1'})
    return result, clock


def test_native_request_queues_exact_duration_and_metadata_atomically(store, policy):
    app, clock = runtime(store, policy)
    assert app.request_time(5) == {'queued': True, 'offline': True}
    batch = store.batch()[1]
    assert len(batch) == 1 and batch[0]['type'] == 'unlock_request' and batch[0]['duration_sec'] == 300
    assert len(batch[0]) == 7 and batch[0]['child_id'] == 'c1'
    request = store.get('time_request')
    assert request['minutes'] == 5 and request['ts'] == batch[0]['ts']
    assert app.request_time(10) == {'queued': False, 'pending': True}
    assert len(store.batch()[1]) == 1
    store.put('child_view', {'day':request['day'],'last_request':{'ts':request['ts'],'status':'acknowledged'}})
    assert app.child_view()['request']['status'] == 'acknowledged'
    assert app.request_time(10)['queued']
    for invalid in [True,0,30,'15']:
        with pytest.raises(ValueError): app.request_time(invalid)


def test_native_local_quota_and_entertainment_are_real_counters(store, policy):
    app, clock = runtime(store, {**policy,'entertainment_quota_sec':100})
    day = app.engine.current_day().date().isoformat()
    with store.transaction() as db:
        db.execute('INSERT INTO usage VALUES (?,60,0)',(day,))
    store.put('entertainment_usage',{day:30})
    app.entertainment.sync_peer_usage(day,20)
    view = app.child_view()
    assert view['remaining_sec'] == 120 and view['entertainment_remaining_sec'] == 50
    assert view['offline'] is True
    store.put('child_view_synced',app.engine.trusted)
    assert app.child_view()['offline'] is False
    store.put('child_view',{'day':'2000-01-01','name':'An','top_apps':[{'subject':'old.exe','value':90}]})
    assert app.child_view()['top_apps'] == []


def test_native_ipc_minutes_stay_behind_peer_authentication():
    received=[]
    ipc=TrayIPC('x'*40,lambda:{},lambda value:None,lambda m:received.append(m) or {'queued':True},port=0,verify_peer=lambda payload,address:payload.get('pid')==123)
    ipc.start()
    try:
        for payload,status in [({'pid':999,'minutes':5},403),({'pid':123,'minutes':True},400),({'pid':123,'minutes':20},400),({'pid':123,'minutes':5},200)]:
            connection=http.client.HTTPConnection('127.0.0.1',ipc.server.server_address[1],timeout=3)
            connection.request('POST','/request-time',json.dumps(payload),{'Authorization':'Bearer '+'x'*40})
            response=connection.getresponse();response.read();assert response.status==status;connection.close()
        assert received==[5]
    finally: ipc.stop()


def test_child_window_friendly_view_model_and_no_false_zero():
    assert presentation({})['remaining'] == 'Đang chờ KidSafe…'
    assert minutes(1)==1 and minutes(0)==0
    view=presentation({'remaining_sec':61,'entertainment_remaining_sec':120,'name':'An',
                       'audit':[{'icon':'unlock','message':'Ba mẹ đã mở khóa máy.','ts':'2026-11-07T01:00:00+00:00'}]})
    assert view['remaining']=='Còn 2 phút' and '🔓' in view['audit'] and '08:00 07/11' in view['audit']


def test_native_request_does_not_mark_pending_when_queue_is_full(store, policy):
    app, _ = runtime(store, policy)
    store.max_events = 0
    with pytest.raises(QueueFull): app.request_time(5)
    assert store.get('time_request') is None


def test_native_cached_transparency_obeys_retention(store, policy):
    app, _ = runtime(store, policy)
    store.put('child_view', {'name':'An','day':'2000-01-01','top_apps':[{'subject':'old.exe','value':30}],
                             'audit':[{'ts':'2000-01-01T00:00:00+00:00','message':'Old'}]})
    store.prune(now=app.engine.trusted)
    view = store.get('child_view')
    assert view == {'name':'An','audit':[]}


def test_native_cache_retention_runs_when_server_is_offline(store, policy):
    app, _ = runtime(store, policy)
    store.put('child_view', {'name':'An','day':'2000-01-01','top_apps':[{'subject':'old.exe','value':30}], 'audit':[]})
    class OneLoop(threading.Event):
        def wait(self, timeout=None):
            self.set()
            return True
    app.stop = OneLoop()
    app.heartbeat = lambda: {}
    def offline(_): raise OSError('offline')
    app.sync.heartbeat = offline
    app.network()
    assert store.get('child_view') == {'name':'An','audit':[]}
