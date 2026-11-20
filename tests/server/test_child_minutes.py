from datetime import datetime, timezone
from zoneinfo import ZoneInfo

from fastapi.testclient import TestClient

from test_backend import auth, child, enroll, lab


def test_child_selected_minutes_follow_request_through_approval_and_ack(lab):
    app, parent = lab
    cid = child(parent)
    route = f"/api/children/{cid}"
    first, _ = enroll(parent, cid)
    second, _ = enroll(parent, cid)
    credentials = {"username": "child-minutes", "password": "minutes-test-123"}
    parent.post(route + "/account", json=credentials).raise_for_status()
    key = {"Idempotency-Key": "choose-minutes-qa"}
    assert parent.post(route + "/requests", json={"minutes": 5}, headers=key).status_code == 403

    with TestClient(app, base_url="https://testserver") as student:
        login = student.post("/api/auth/login", json=credentials)
        login.raise_for_status()
        student.headers["X-CSRF-Token"] = login.json()["csrf_token"]
        assert student.post(route + "/requests", json={"minutes": 20}, headers=key).status_code == 422
        student.post(route + "/requests", json={"minutes": 5}, headers=key).raise_for_status()
        pending = parent.get(route + "/reports").json()["pending_requests"]
        assert len(pending) == 1 and pending[0]["requested_minutes"] == 5
        request = pending[0]
        target, peer = (first, second) if request["device_id"] == first["device_id"] else (second, first)
        # A retry still belongs to the original request even if the most recently seen machine changes.
        day = datetime.now(timezone.utc).astimezone(ZoneInfo("Asia/Ho_Chi_Minh")).date().isoformat()
        parent.post("/api/device/heartbeat", headers=auth(peer), json={
            "device_id": peer["device_id"], "status": "active", "quota_used_sec": 0,
            "policy_version": 1, "usage_date": day,
        }).raise_for_status()
        assert student.post(route + "/requests", json={"minutes": 5}, headers=key).json()["duplicate"]
        assert student.post(route + "/requests", json={"minutes": 10}, headers=key).status_code == 409

    device_id = target["device_id"]
    command = {"device_id": device_id, "type": "add_time"}
    approval_key = {"Idempotency-Key": f"request-{device_id}-{request['ts']}"}
    approved = parent.post(route + "/commands", json=command, headers=approval_key)
    approved.raise_for_status()
    payload = approved.json()["payload"]
    assert payload["seconds"] == 300
    assert parent.post(route + "/commands", json=command, headers=approval_key).json() == approved.json()
    assert parent.get(route + "/reports").json()["pending_extra_seconds"] == 300
    parent.post(f"/api/device/commands/{payload['id']}/ack", headers=auth(target), json={}).raise_for_status()
    report = parent.get(route + "/reports").json()
    assert report["extra_granted_seconds"] == 300
    assert report["requests"][0]["status"] == "acknowledged"
    assert parent.get(route + "/audit/recent").json()[0]["message"] == "Bố mẹ đã gửi lệnh cộng thêm 5 phút sử dụng."
