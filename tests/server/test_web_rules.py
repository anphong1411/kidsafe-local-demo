import pytest
from fastapi.testclient import TestClient

from agent.dns_proxy import matches
from test_backend import auth, child, enroll, lab


@pytest.mark.parametrize(("host", "expected"), [
    ("WWW.YouTube.COM.", "youtube.com"),
    ("store.example.co.uk", "example.co.uk"),
    ("www.example.github.io", "example.github.io"),
    ("github.io", "github.io"),
    ("www.xn--bcher-kva.de", "xn--bcher-kva.de"),
    ("co.uk", None),
    ("192.0.2.1", None),
    ("bad..example.com", None),
    ("https://example.com/private?q=1", None),
])
def test_website_normalization(lab, host, expected):
    _, client = lab
    route = f"/api/children/{child(client)}/web/domain"
    result = client.get(route, params={"host": host})
    if expected is None:
        assert result.status_code == 422
    else:
        assert result.json() == {"domain": expected}


def test_web_updates_are_scoped_signed_idempotent_and_keep_other_policy(lab):
    app, client = lab
    cid = child(client)
    route = f"/api/children/{cid}/web"
    policy_url = f"/api/children/{cid}/policy"
    original = client.get(policy_url).json()["policy"]
    original["blocked_domains"] = ["legacy.example.org", "example.org"]
    original["weekday_quota_sec"] = 6000
    client.put(policy_url, json=original).raise_for_status()

    with TestClient(app, base_url="https://testserver") as other:
        login = other.post("/api/auth/login", json={"username": "parent2", "password": "correct-pass2"})
        other.headers["X-CSRF-Token"] = login.json()["csrf_token"]
        assert other.get(route + "/domain", params={"host": "example.com"}).status_code == 404
        assert other.patch(route, json={"action": "safesearch", "enabled": False}).status_code == 404

    def change(**body):
        response = client.patch(route, json=body)
        response.raise_for_status()
        return response.json()

    assert client.patch(route, json={"action": "add_domain", "host": "https://example.com/watch"}).status_code == 422
    change(action="category", category="games", enabled=True)
    change(action="safesearch", enabled=False)
    added = change(action="add_domain", host="www.shop.example.co.uk")
    assert added["blocked_domains"] == ["legacy.example.org", "example.org", "example.co.uk"]
    assert change(action="add_domain", host="example.co.uk")["version"] == added["version"]
    removed = change(action="remove_domain", host="legacy.example.org")
    assert removed["blocked_domains"] == ["example.org", "example.co.uk"]

    current = client.get(policy_url).json()
    assert current["version"] == removed["version"]
    assert current["policy"]["weekday_quota_sec"] == 6000
    assert current["policy"]["app_groups"] == original["app_groups"]
    device, _ = enroll(client, cid)
    payload = client.get("/api/device/policy", headers=auth(device)).json()["payload"]
    assert "games" in payload["blocked_categories"] and not payload["safesearch"]
    assert any(matches("www.shop.example.co.uk", rule) for rule in payload["blocked_domains"])
    assert "legacy.example.org" not in payload["blocked_domains"]
    audit = [item for item in client.get(f"/api/children/{cid}/audit").json() if item["action"] == "update_web_rules"]
    assert len(audit) == 4
    assert any(item["new"]["blocked_domains"] == removed["blocked_domains"] for item in audit)
