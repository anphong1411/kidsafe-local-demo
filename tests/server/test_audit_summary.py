from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

from server.app import now
from server.audit_summary import summarize_audit
from test_backend import child, enroll, lab


def test_recent_audit_translates_changes_orders_ties_and_scopes_children(lab, monkeypatch):
    app, client = lab
    epoch = now()
    monkeypatch.setattr("server.app.now", lambda: epoch)
    cid = child(client)
    base = f"/api/children/{cid}"
    credentials = {"username": "timeline-student", "password": "timeline-pass-123"}
    client.post(base + "/account", json=credentials).raise_for_status()
    device, _ = enroll(client, cid)
    policy = client.get(base + "/policy").json()["policy"]

    def save_policy():
        client.put(base + "/policy", json=policy).raise_for_status()

    policy["weekday_quota_sec"] = 9000
    save_policy()
    policy["schedule"][0][0] = False
    save_policy()
    policy["app_groups"]["study"]["apps"] = [{"name": "study.exe", "sha256": "a" * 64}]
    save_policy()
    policy["app_groups"]["blocked"]["apps"] = [{"name": "blocked.exe", "sha256": "b" * 64}]
    save_policy()
    policy["app_groups"]["study"]["apps"] = []
    save_policy()
    client.patch(base + "/web", json={"action": "category", "category": "games", "enabled": True}).raise_for_status()
    client.patch(base + "/web", json={"action": "add_domain", "host": "example.org"}).raise_for_status()
    for kind in ("lock", "unlock", "add_time"):
        client.post(base + "/commands", headers={"Idempotency-Key": uuid4().hex},
                    json={"type": kind, "device_id": device["device_id"]}).raise_for_status()

    recent = client.get(base + "/audit/recent").json()
    assert len(recent) == 10 and all(set(item) == {"ts", "icon", "message"} for item in recent)
    assert len({item["ts"] for item in recent}) == 1
    assert [item["icon"] for item in recent] == [
        "unlock", "unlock", "lock", "lock", "lock", "settings", "lock", "settings", "clock", "unlock",
    ]
    assert [item["message"] for item in recent] == [
        "Bố mẹ đã gửi lệnh cộng thêm 15 phút sử dụng.",
        "Bố mẹ đã gửi lệnh mở khóa tạm thời.",
        "Bố mẹ đã gửi lệnh khóa máy.",
        "Bố mẹ đã chặn riêng tên miền example.org.",
        "Bố mẹ đã chặn danh mục website Trò chơi.",
        "Ứng dụng study.exe đã được gỡ khỏi nhóm Học tập.",
        "Ứng dụng blocked.exe đã bị chặn.",
        "Ứng dụng study.exe đã được đưa vào nhóm Học tập.",
        "Lịch sử dụng trong tuần đã được cập nhật.",
        "Hạn mức ngày thường đã thay đổi từ 120 phút thành 150 phút.",
    ]
    with TestClient(app, base_url="https://testserver") as viewer:
        viewer.post("/api/auth/login", json=credentials).raise_for_status()
        assert viewer.get(base + "/audit/recent").json() == recent
        viewer.post("/api/auth/login", json={"username": "parent2", "password": "correct-pass2"}).raise_for_status()
        assert viewer.get(base + "/audit/recent").status_code == 404


@pytest.mark.parametrize(("action", "old", "new", "icon", "wording"), [
    ("update_web_rules", {"blocked_domains": ["example.org"]}, {"blocked_domains": []}, "unlock", "bỏ chặn"),
    ("update_web_rules", {"safesearch": True}, {"safesearch": False}, "lock", "tắt"),
    ("update_web_rules", {"safesearch": False}, {"safesearch": True}, "unlock", "bật"),
    ("update_policy", {"weekday_quota_sec": 7200}, {"weekday_quota_sec": 3600}, "lock", "120 phút thành 60 phút"),
    ("update_policy", {"app_groups": {"games": {"enabled": True}}},
     {"app_groups": {"games": {"enabled": False}}}, "lock", "tắt nhóm Trò chơi"),
    ("update_web_rules", {"blocked_domains": ["example.org"]}, {"blocked_domains": ["example.com"]},
     "settings", "bỏ chặn"),
])
def test_recent_icons_distinguish_lock_unlock_and_mixed_changes(action, old, new, icon, wording):
    actual_icon, message = summarize_audit(action, old, new)
    assert actual_icon == icon
    assert wording in message
