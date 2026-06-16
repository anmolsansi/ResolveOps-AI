"""Tests for V10a security admin."""
from fastapi.testclient import TestClient


def _setup(client: TestClient) -> tuple[str, str]:
    resp = client.post(
        "/auth/register",
        json={"email": "security-test@example.com", "password": "password123"},
    )
    token = resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    ws_resp = client.post("/workspaces", json={"name": "Security Test WS"}, headers=headers)
    ws_id = ws_resp.json()["id"]
    return token, ws_id


class TestApiKeys:
    def test_create_key(self, client: TestClient):
        token, _ = _setup(client)
        headers = {"Authorization": f"Bearer {token}"}
        resp = client.post(
            "/security/api-keys",
            json={"name": "Test Key", "scopes": ["read", "write"]},
            headers=headers,
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["name"] == "Test Key"
        assert data["raw_key"].startswith("ro_")
        assert len(data["key_prefix"]) > 0

    def test_list_keys(self, client: TestClient):
        token, _ = _setup(client)
        headers = {"Authorization": f"Bearer {token}"}
        client.post("/security/api-keys", json={"name": "Key1"}, headers=headers)
        resp = client.get("/security/api-keys", headers=headers)
        assert resp.status_code == 200
        assert resp.json()["total"] >= 1

    def test_revoke_key(self, client: TestClient):
        token, _ = _setup(client)
        headers = {"Authorization": f"Bearer {token}"}
        create = client.post("/security/api-keys", json={"name": "Revoke me"}, headers=headers)
        kid = create.json()["id"]
        resp = client.delete(f"/security/api-keys/{kid}", headers=headers)
        assert resp.status_code == 200

    def test_revoke_not_found(self, client: TestClient):
        token, _ = _setup(client)
        headers = {"Authorization": f"Bearer {token}"}
        fake = "00000000-0000-0000-0000-000000000000"
        resp = client.delete(f"/security/api-keys/{fake}", headers=headers)
        assert resp.status_code == 404


class TestRateLimits:
    def test_get_rate_limits(self, client: TestClient):
        token, _ = _setup(client)
        headers = {"Authorization": f"Bearer {token}"}
        resp = client.get("/security/rate-limits", headers=headers)
        assert resp.status_code == 200
        assert "requests_per_minute" in resp.json()

    def test_update_rate_limits(self, client: TestClient):
        token, _ = _setup(client)
        headers = {"Authorization": f"Bearer {token}"}
        resp = client.put(
            "/security/rate-limits",
            json={"requests_per_minute": 120},
            headers=headers,
        )
        assert resp.status_code == 200
        assert resp.json()["requests_per_minute"] == 120


class TestLoginAttempts:
    def test_list_empty(self, client: TestClient):
        token, _ = _setup(client)
        headers = {"Authorization": f"Bearer {token}"}
        resp = client.get("/security/login-attempts", headers=headers)
        assert resp.status_code == 200
        assert "items" in resp.json()


class TestIpAllowlist:
    def test_add_ip(self, client: TestClient):
        token, _ = _setup(client)
        headers = {"Authorization": f"Bearer {token}"}
        resp = client.post(
            "/security/ip-allowlist",
            json={"ip_address": "10.0.0.1", "note": "Office"},
            headers=headers,
        )
        assert resp.status_code == 200
        assert resp.json()["ip_address"] == "10.0.0.1"

    def test_list_ips(self, client: TestClient):
        token, _ = _setup(client)
        headers = {"Authorization": f"Bearer {token}"}
        client.post("/security/ip-allowlist", json={"ip_address": "10.0.0.2"}, headers=headers)
        resp = client.get("/security/ip-allowlist", headers=headers)
        assert resp.status_code == 200
        assert resp.json()["total"] >= 1

    def test_remove_ip(self, client: TestClient):
        token, _ = _setup(client)
        headers = {"Authorization": f"Bearer {token}"}
        create = client.post(
            "/security/ip-allowlist",
            json={"ip_address": "10.0.0.3"},
            headers=headers,
        )
        eid = create.json()["id"]
        resp = client.delete(f"/security/ip-allowlist/{eid}", headers=headers)
        assert resp.status_code == 200


class TestSecuritySettings:
    def test_get_settings(self, client: TestClient):
        token, _ = _setup(client)
        headers = {"Authorization": f"Bearer {token}"}
        resp = client.get("/security/settings", headers=headers)
        assert resp.status_code == 200
        data = resp.json()
        assert "rate_limit_requests_per_minute" in data
        assert "ip_allowlist_enabled" in data

    def test_update_settings(self, client: TestClient):
        token, _ = _setup(client)
        headers = {"Authorization": f"Bearer {token}"}
        resp = client.put(
            "/security/settings",
            json={"max_login_attempts": 10, "ip_allowlist_enabled": True},
            headers=headers,
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["max_login_attempts"] == 10
        assert data["ip_allowlist_enabled"] is True
