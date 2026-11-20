import csv
from datetime import datetime
from io import StringIO
from uuid import uuid4
from zoneinfo import ZoneInfo

from fastapi.testclient import TestClient

from test_backend import auth, child, enroll, event, lab


def test_hyphenated_pairing_code_is_single_use(lab):
    _, client = lab
    cid = child(client)
    code = client.post(f"/api/children/{cid}/enroll-codes", json={"consent": True}).json()
    assert code["expires_in"] == 600 and len(code["code"]) == 8
    value = code["code"]
    enrollment = {"code": value[:4] + "-" + value[4:], "fingerprint": uuid4().hex, "name": "QA"}
    assert client.post("/api/device/enroll", json=enrollment).status_code == 201
    assert client.post("/api/device/enroll", json=enrollment).status_code == 400


def test_reset_child_password_revokes_sessions_and_audits_without_password(lab):
    app, client = lab
    cid = child(client)
    path = f"/api/children/{cid}/account"
    assert client.get(path).json() == {"username": None}
    user = "student"
    credentials = {"username": user, "password": "old-pass-123"}
    client.post(path, json=credentials).raise_for_status()
    assert client.get(path).json() == {"username": user}
    with TestClient(app, base_url="https://testserver") as student:
        login = student.post("/api/auth/login", json=credentials)
        login.raise_for_status()
        student.headers["X-CSRF-Token"] = login.json()["csrf_token"]
        new_password = {"password": "new-pass-123"}
        assert student.put(path + "/password", json=new_password).status_code == 403
        client.put(path + "/password", json=new_password).raise_for_status()
        assert student.get("/api/auth/me").status_code == 401
        assert student.post("/api/auth/login", json=credentials).status_code == 401
        assert student.post("/api/auth/login", json={"username": user, **new_password}).status_code == 200
        assert student.get(f"/api/children/{cid}/reports.csv").status_code == 403
    audit = next(row for row in client.get(f"/api/children/{cid}/audit").json() if row["action"] == "reset_child_password")
    assert audit["new"] == {"username": user, "sessions_revoked": True}


def test_csv_matches_scoped_week_report_and_escapes_spreadsheet_formula(lab):
    _, client = lab
    cid = child(client)
    device, _ = enroll(client, cid)
    day = datetime.now(ZoneInfo("Asia/Ho_Chi_Minh")).date().isoformat()
    headers = auth(device)
    client.post("/api/device/heartbeat", headers=headers, json={
        "device_id": device["device_id"], "status": "active", "quota_used_sec": 120,
        "exception_used_sec": 30, "entertainment_used_sec": 45, "policy_version": 1, "usage_date": day,
    }).raise_for_status()
    events = [event(device, type="app_stop", subject="=example.exe", duration_sec=90), event(device)]
    client.post("/api/device/events", headers={**headers, "Idempotency-Key": uuid4().hex},
                json={"events": events}).raise_for_status()
    path = f"/api/children/{cid}/reports.csv"
    response = client.get(path)
    response.raise_for_status()
    assert response.headers["content-disposition"].endswith(f'kidsafe-report-{day}.csv"')
    assert response.headers["cache-control"] == "no-store"
    rows = list(csv.DictReader(StringIO(response.content.decode("utf-8-sig"))))
    daily = [row for row in rows if row["Loại"] == "Thời lượng"]
    assert len(daily) == 7
    assert [daily[-1][key] for key in ("Ngày", "Tổng giây", "Giây ngoại lệ", "Giây giải trí")] == [day, "150", "30", "45"]
    assert any(row["Mục"] == "'=example.exe" and row["Tổng giây"] == "90" for row in rows)
    assert any(row["Mục"] == "example.com" and row["Lượt truy vấn"] == "1" for row in rows)


def test_server_signs_unlock_until_child_local_midnight(lab):
    _, client = lab
    cid = child(client)
    device, _ = enroll(client, cid)
    response = client.post(f"/api/children/{cid}/commands", headers={"Idempotency-Key": "daily-unlock-qa"},
                           json={"device_id": device["device_id"], "type": "unlock"})
    response.raise_for_status()
    payload = response.json()["payload"]
    zone = ZoneInfo("Asia/Ho_Chi_Minh")
    issued = datetime.fromisoformat(payload["issued_at"]).astimezone(zone)
    expires = datetime.fromisoformat(payload["expires_at"]).astimezone(zone)
    assert payload["mode"] == "until_midnight" and "seconds" not in payload
    assert (expires.date() - issued.date()).days == 1 and expires.time().isoformat() == "00:00:00"
