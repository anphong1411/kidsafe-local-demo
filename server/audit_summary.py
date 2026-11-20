"""Translate stored audit snapshots into short, child-friendly descriptions."""

CATEGORIES = {
    "education": "Giáo dục", "entertainment": "Giải trí", "social": "Mạng xã hội",
    "games": "Trò chơi", "age_inappropriate": "Không phù hợp lứa tuổi", "unclassified": "Chưa phân loại",
}
GROUPS = {
    "study": "Học tập", "games": "Trò chơi", "video": "Xem video & Giải trí",
    "social": "Mạng xã hội & Trình duyệt", "blocked": "Ứng dụng chặn tuyệt đối",
}
QUOTAS = {
    "weekday_quota_sec": "Hạn mức ngày thường", "weekend_quota_sec": "Hạn mức cuối tuần",
    "entertainment_quota_sec": "Hạn mức giải trí",
}
MESSAGES = {
    "command_lock": ("lock", "Bố mẹ đã gửi lệnh khóa máy."),
    "command_unlock": ("unlock", "Bố mẹ đã gửi lệnh mở khóa tạm thời."),
    "create_child": ("settings", "Bố mẹ đã tạo hồ sơ cho con."),
    "create_child_account": ("settings", "Bố mẹ đã tạo tài khoản đăng nhập cho con."),
    "reset_child_password": ("settings", "Bố mẹ đã làm mới mật khẩu đăng nhập của con."),
    "parental_consent": ("device", "Bố mẹ đã tạo mã ghép đôi cho máy của con."),
    "revoke_device": ("lock", "Bố mẹ đã thu hồi quyền kết nối của một máy."),
    "budget_transfer_requested": ("clock", "Bố mẹ đã yêu cầu chuyển phần giờ sử dụng giữa các máy."),
    "allocate_unreserved_budget": ("clock", "Bố mẹ đã cấp thêm phần giờ có thể dùng khi máy mất mạng."),
    "return_budget_requested": ("clock", "Bố mẹ đã yêu cầu một máy trả lại phần giờ được giữ."),
    "allocation_changed": ("clock", "Phần giờ có thể dùng khi máy mất mạng đã thay đổi."),
    "upgrade_app_groups": ("settings", "KidSafe đã bổ sung cấu hình nhóm ứng dụng."),
    "upgrade_entertainment_policy": ("clock", "KidSafe đã cập nhật cấu hình hạn mức giải trí."),
}


def _minutes(seconds):
    return f"{seconds / 60:.2f}".rstrip("0").rstrip(".").replace(".", ",") + " phút"


def _names(values):
    names = list(values)
    preview = ", ".join(names[:3])
    return f"{preview} và {len(names) - 3} mục khác" if len(names) > 3 else preview


def _list_delta(before, after, added, removed):
    changes = []
    if new := sorted(set(after) - set(before)):
        changes.append(added.format(_names(new)))
    if gone := sorted(set(before) - set(after)):
        changes.append(removed.format(_names(gone)))
    return changes


def _block_directions(before, after):
    old, new = set(before), set(after)
    directions = set()
    if new - old:
        directions.add("lock")
    if old - new:
        directions.add("unlock")
    return directions


def _web_changes(old, new):
    directions = set()
    for field in ("blocked_categories", "blocked_domains"):
        directions.update(_block_directions(old.get(field, []), new.get(field, [])))
    changes = _list_delta(
        [CATEGORIES[key] for key in old.get("blocked_categories", []) if key in CATEGORIES],
        [CATEGORIES[key] for key in new.get("blocked_categories", []) if key in CATEGORIES],
        "Bố mẹ đã chặn danh mục website {}.", "Bố mẹ đã bỏ chặn danh mục website {}.",
    )
    changes += _list_delta(old.get("blocked_domains", []), new.get("blocked_domains", []),
                           "Bố mẹ đã chặn riêng tên miền {}.", "Bố mẹ đã bỏ chặn riêng tên miền {}.")
    if old.get("safesearch") != new.get("safesearch") and "safesearch" in new:
        changes.append("Bố mẹ đã " + ("bật" if new["safesearch"] else "tắt") + " tìm kiếm an toàn.")
        directions.add("unlock" if new["safesearch"] else "lock")
    return changes, directions


def _apps_by_name(rules):
    return {rule["name"].casefold(): rule for rule in rules}


def _app_changes(old, new):
    changes = []
    directions = set()
    old_groups, new_groups = old.get("app_groups", {}), new.get("app_groups", {})
    for key, label in GROUPS.items():
        before, after = old_groups.get(key, {}), new_groups.get(key, {})
        old_apps, new_apps = _apps_by_name(before.get("apps", [])), _apps_by_name(after.get("apps", []))
        if key == "blocked":
            directions.update(_block_directions(old_apps, new_apps))
        elif "enabled" in before and "enabled" in after and before["enabled"] != after["enabled"]:
            enabled = after["enabled"]
            directions.add("unlock" if enabled else "lock")
            changes.append(f"Bố mẹ đã {'bật' if enabled else 'tắt'} nhóm {label}.")
        old_limit, new_limit = before.get("quota_sec"), after.get("quota_sec")
        if isinstance(old_limit, int) and isinstance(new_limit, int) and old_limit != new_limit:
            directions.add("unlock" if new_limit > old_limit else "lock")
        if added := sorted(new_apps.keys() - old_apps.keys()):
            names = _names(new_apps[name]["name"] for name in added)
            changes.append(f"Ứng dụng {names} đã bị chặn." if key == "blocked"
                           else f"Ứng dụng {names} đã được đưa vào nhóm {label}.")
        if removed := sorted(old_apps.keys() - new_apps.keys()):
            names = _names(old_apps[name]["name"] for name in removed)
            changes.append(f"Ứng dụng {names} đã được bỏ chặn." if key == "blocked"
                           else f"Ứng dụng {names} đã được gỡ khỏi nhóm {label}.")
        if any(before.get(field) != after.get(field) for field in ("mode", "quota_sec", "window", "message")):
            changes.append(f"Quy tắc của nhóm {label} đã thay đổi.")
        elif any(old_apps[name] != new_apps[name] for name in old_apps.keys() & new_apps.keys()):
            changes.append(f"Thông tin nhận diện ứng dụng trong nhóm {label} đã thay đổi.")
    old_rules, new_rules = _apps_by_name(old.get("apps", [])), _apps_by_name(new.get("apps", []))
    if new.get("app_mode") == "blocklist" and old.get("app_mode") == "blocklist":
        directions.update(_block_directions(old_rules, new_rules))
        changes += _list_delta(old_rules, new_rules, "Ứng dụng {} đã bị chặn.", "Ứng dụng {} đã được bỏ chặn.")
    if (old_rules != new_rules or old.get("app_mode") != new.get("app_mode")) and not changes:
        changes.append("Danh sách ứng dụng được phép hoặc bị chặn đã thay đổi.")
    changes += _list_delta(old.get("entertainment_apps", []), new.get("entertainment_apps", []),
                           "Ứng dụng {} đã được đưa vào nhóm Trò chơi.",
                           "Ứng dụng {} đã được gỡ khỏi nhóm Trò chơi.")
    return changes, directions


def summarize_audit(action, old, new):
    if action == "command_add_time":
        seconds = (new or {}).get("seconds", 900)
        return "unlock", f"Bố mẹ đã gửi lệnh cộng thêm {_minutes(seconds)} sử dụng."
    if action in MESSAGES:
        return MESSAGES[action]
    if action not in ("update_policy", "update_web_rules"):
        return "settings", "Cài đặt liên quan đến con đã được cập nhật."
    old, new = old or {}, new or {}
    quota_keys = [key for key in QUOTAS if key in old and key in new and old[key] != new[key]]
    quota = [f"{QUOTAS[key]} đã thay đổi từ {_minutes(old[key])} thành {_minutes(new[key])}." for key in quota_keys]
    directions = {"unlock" if new[key] > old[key] else "lock" for key in quota_keys}
    schedule = ["Lịch sử dụng trong tuần đã được cập nhật."] if old.get("schedule") != new.get("schedule") else []
    web, web_directions = _web_changes(old, new)
    apps, app_directions = _app_changes(old, new)
    directions.update(web_directions | app_directions)
    changes = quota + schedule + apps + web
    if old.get("timezone") != new.get("timezone"):
        changes.append("Múi giờ sử dụng đã thay đổi.")
    if not changes:
        return "settings", "Bố mẹ đã lưu cài đặt của con."
    icon = next(iter(directions)) if len(directions) == 1 else "clock" if schedule and not directions else "settings"
    text = " ".join(changes[:3])
    if len(changes) > 3:
        text += f" Cùng {len(changes) - 3} thay đổi khác."
    return icon, text
