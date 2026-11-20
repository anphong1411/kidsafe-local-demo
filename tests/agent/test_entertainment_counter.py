from datetime import datetime, timedelta, timezone
from hashlib import sha256
from threading import RLock
from types import SimpleNamespace

from agent.app_groups import AppGroups
from agent.apps import AppMonitor, AppRules
from agent.entertainment import EntertainmentCounter
from agent.runtime import Runtime
from agent.storage import Store


def test_group_counter_is_explicit_independent_durable_and_splits_local_midnight(tmp_path):
    path = tmp_path / 'counter.db'
    store = Store(path)
    counter = EntertainmentCounter(store)
    # 00:00:01 local, so a two-second interval crosses the day boundary.
    end = datetime(2026, 11, 5, 17, 0, 1, tzinfo=timezone.utc).timestamp()
    counter.record('school.exe', 2, end, ['game.exe'], 'Asia/Ho_Chi_Minh')
    assert counter.used('2026-11-06') == 0
    counter.record('GAME.EXE', 2, end, ['game.exe'], 'Asia/Ho_Chi_Minh')
    assert counter.used('2026-11-05') == 1 and counter.used('2026-11-06') == 1
    counter.record('game.exe', 8, end + 8, ['game.exe'], 'Asia/Ho_Chi_Minh')
    assert counter.used('2026-11-06') == 1  # suspend/stall is not active use
    for i in range(4):
        counter.record('game.exe', .25, end + i + 1, ['game.exe'], 'Asia/Ho_Chi_Minh')
    assert counter.used('2026-11-06') == 2
    assert store.db.execute('SELECT COUNT(*) FROM usage').fetchone()[0] == 0
    store.close()
    reopened = Store(path)
    assert EntertainmentCounter(reopened).used('2026-11-06') == 2
    reopened.close()


def test_counter_cannot_resume_collection_after_deletion(tmp_path):
    store = Store(tmp_path / 'deleted.db')
    store.put('deletion_generation', 1)
    EntertainmentCounter(store).record('game.exe', 2, 1793898002, ['game.exe'], 'Asia/Ho_Chi_Minh')
    assert store.get('entertainment_usage') is None
    store.close()


def test_foreground_monitor_does_not_count_idle_locked_or_stalled_time(tmp_path):
    path = tmp_path / 'game.exe'
    path.write_bytes(b'fixture only, never executed')
    clock = [0]
    charged = []

    class Process:
        pid = 987654
        def username(self): return r'LAB\child'
        def exe(self): return str(path)
        def name(self): return 'game.exe'
        def create_time(self): return 10
        def terminate(self): raise AssertionError('No native action is authorized by this test')

    monitor = AppMonitor(r'LAB\child', AppRules('blocklist', []), lambda *args: None, lambda name: True,
                         processes=lambda: [Process()], monotonic=lambda: clock[0],
                         on_usage=lambda name, digest, seconds: charged.append((name, seconds)))
    monitor.tick(Process.pid, active=True)
    clock[0] += 2
    monitor.tick(Process.pid, active=True)
    clock[0] += 1
    monitor.tick(0, active=False, enforce=False)
    clock[0] += 1
    monitor.tick(Process.pid, active=True)
    clock[0] += 10
    monitor.tick(Process.pid, active=True)
    assert charged == [('game.exe', 2)]


def test_exhaustion_blocks_only_selected_apps_after_visible_ack(tmp_path):
    runtime = Runtime.__new__(Runtime)
    runtime.guard = RLock()
    runtime.store = Store(tmp_path / 'limit.db')
    runtime.entertainment = EntertainmentCounter(runtime.store)
    current = datetime(2026, 11, 5, 20, tzinfo=timezone.utc)
    runtime.engine = SimpleNamespace(current_day=lambda: current, trusted=current.timestamp())
    games = {'name': 'game.exe', 'sha256': sha256(b'renamed-game.exe').hexdigest()}
    video = {'name': 'video.exe', 'sha256': sha256(b'video.exe').hexdigest()}
    study = {'name': 'school.exe', 'sha256': sha256(b'school.exe').hexdigest()}
    runtime.policy = dict(timezone='UTC', entertainment_quota_sec=4,
                          weekday_quota_sec=600, weekend_quota_sec=600,
                          app_groups={'games': {'mode': 'entertainment', 'apps': [games], 'message': 'Hãy nghỉ nhé.'},
                                      'video': {'mode': 'entertainment', 'apps': [video]},
                                      'study': {'mode': 'daily', 'apps': [study]}})
    runtime.app_groups = AppGroups(runtime.policy)
    runtime.explanation = runtime.explanation_ack = None
    runtime.entertainment.sync_peer_usage('2026-11-05', 2)
    runtime.entertainment.sync_peer_usage('2026-11-05', 1)  # older heartbeat
    clock, events, terminated = [0], [], []

    class Process:
        def __init__(self, pid, name):
            self.pid, self.filename = pid, tmp_path / name
            self.filename.write_bytes(name.encode())  # fixture, never executed
        def username(self): return r'LAB\child'
        def exe(self): return str(self.filename)
        def name(self): return self.filename.name
        def create_time(self): return 1
        def terminate(self): terminated.append(self.name())

    game = Process(987654, 'renamed-game.exe')
    video_process = Process(987655, 'video.exe')
    school = Process(987656, 'school.exe')
    monitor = AppMonitor(
        r'LAB\child', AppRules('blocklist', []), lambda *event: events.append(event), runtime.explain,
        processes=lambda: [game, video_process, school], monotonic=lambda: clock[0], on_usage=runtime.record_group_usage,
        group_block=runtime.group_block, explain_group=runtime.explain_group,
    )
    monitor.tick(game.pid, active=True)
    assert runtime.explanation is None
    clock[0] += 2
    monitor.tick(game.pid, active=True)
    assert runtime.entertainment.used('2026-11-05') == 2
    assert not terminated and 'hết giờ giải trí' in runtime.explanation['text']
    assert 'Hãy nghỉ nhé.' in runtime.explanation['text']
    runtime.explanation_ack = runtime.explanation['id']
    monitor.tick(school.pid, active=True)
    assert terminated == ['renamed-game.exe']
    assert ('blocked_app', 'renamed-game.exe', 0) in events and monitor.foreground[0] == school.pid
    runtime.explanation_ack = runtime.explanation['id']
    monitor.tick(school.pid, active=True)
    assert 'video.exe' in terminated
    assert runtime.entertainment.group_used('2026-11-05') == {'games': 2}
    current += timedelta(days=1)
    assert not runtime.group_block('game.exe', '')
    runtime.policy['entertainment_quota_sec'] = 0
    runtime.app_groups = AppGroups(runtime.policy)
    assert runtime.group_block('game.exe', '') and not runtime.group_block('school.exe', '')
    runtime.store.close()


def test_group_window_custom_quota_and_absolute_block(tmp_path):
    store = Store(tmp_path / 'groups.db')
    counter = EntertainmentCounter(store)
    groups = AppGroups({
        'weekday_quota_sec': 7200, 'weekend_quota_sec': 7200,
        'app_groups': {
            'social': {'mode': 'custom', 'quota_sec': 120, 'apps': [{'name': 'browser.exe', 'sha256': 'a'*64}],
                       'window': {'days': [5], 'start_minute': 1080, 'end_minute': 1260}},
            'blocked': {'apps': [{'name': 'blocked.exe', 'sha256': 'b'*64}]},
            'study': {'enabled': False, 'apps': [{'name': 'school.exe', 'sha256': 'c'*64}]},
        },
    })
    saturday = datetime(2026, 11, 7, 18, tzinfo=timezone.utc)
    assert not groups.block_notice('browser.exe', 'a'*64, saturday, counter)
    assert 'ngoài khung giờ' in groups.block_notice('browser.exe', '', saturday - timedelta(minutes=1), counter)[1]
    assert 'ngoài khung giờ' in groups.block_notice('browser.exe', '', saturday + timedelta(hours=3), counter)[1]
    assert groups.block_notice('renamed.exe', 'b'*64, saturday, counter)
    assert groups.block_notice('school.exe', '', saturday, counter)
    counter.sync_peer_usage('2026-11-07', 0, {'social': 118})
    counter.record_interval(2, saturday.timestamp()+2, 'UTC', group='social')
    assert 'hết thời gian' in groups.block_notice('browser.exe', '', saturday, counter)[1]
    assert counter.used('2026-11-07') == 0
    store.close()
