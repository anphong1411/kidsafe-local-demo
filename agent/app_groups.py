"""Match signed group rules and enforce them using the trusted local calendar."""

GROUP_NAMES = {
    'study': 'Học tập', 'games': 'Trò chơi', 'video': 'Xem video & Giải trí',
    'social': 'Mạng xã hội & Trình duyệt', 'blocked': 'Ứng dụng chặn tuyệt đối',
}


class AppGroups:
    def __init__(self, policy):
        self.groups = policy.get('app_groups', {})
        self.names = {app['name'].casefold(): key for key, group in self.groups.items() for app in group['apps']}
        self.hashes = {app['sha256'].lower(): key for key, group in self.groups.items() for app in group['apps']}
        self.legacy = set(policy.get('entertainment_apps', []))
        self.quota = min(policy.get('entertainment_quota_sec', 3600),
                         policy['weekday_quota_sec'], policy['weekend_quota_sec'])

    def matches(self, name, digest):
        name = name.casefold()
        named = self.names.get(name)
        if named is None and name in self.legacy:
            named = 'games'
        hashed = self.hashes.get(digest)
        return tuple(dict.fromkeys(key for key in (hashed, named) if key is not None))

    def mode(self, key):
        return self.groups.get(key, {}).get('mode', 'entertainment' if key == 'games' else 'daily')

    def block_notice(self, name, digest, now, counter):
        matches = self.matches(name, digest)
        if 'blocked' in matches:
            matches = ('blocked',)
        day = now.date().isoformat()
        minute = now.hour * 60 + now.minute
        for key in matches:
            group = self.groups.get(key, {})
            label = GROUP_NAMES[key]
            window = group.get('window')
            if key == 'blocked' or not group.get('enabled', True):
                reason = f'Nhóm {label} đang được phụ huynh khóa.'
            elif window and (now.weekday() not in window['days'] or not window['start_minute'] <= minute < window['end_minute']):
                reason = f'Nhóm {label} hiện ngoài khung giờ được phép.'
            elif self.mode(key) == 'entertainment' and counter.exhausted(day, self.quota):
                reason = f'Em đã dùng hết giờ giải trí hôm nay. Nhóm {label} tạm khóa.'
            elif self.mode(key) == 'custom' and counter.exhausted(day, group['quota_sec'], key):
                reason = f'Em đã dùng hết thời gian của nhóm {label} hôm nay.'
            else:
                continue
            message = group.get('message', '').strip()
            return label, f'{reason}\n{message}' if message else reason
        return None
