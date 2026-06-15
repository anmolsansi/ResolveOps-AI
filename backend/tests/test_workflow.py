"""Tests for V9 workflow automation and self-service portal."""
from fastapi.testclient import TestClient


def _setup(client: TestClient) -> tuple[str, str]:
    resp = client.post(
        "/auth/register",
        json={"email": "workflow-test@example.com", "password": "password123"},
    )
    token = resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    ws_resp = client.post("/workspaces", json={"name": "Workflow Test WS"}, headers=headers)
    ws_id = ws_resp.json()["id"]
    return token, ws_id


class TestRoutingRules:
    def test_list_empty(self, client: TestClient):
        token, ws_id = _setup(client)
        headers = {"Authorization": f"Bearer {token}"}
        resp = client.get("/workflow/routing", headers=headers)
        assert resp.status_code == 200
        assert resp.json()["total"] == 0

    def test_create_rule(self, client: TestClient):
        token, ws_id = _setup(client)
        headers = {"Authorization": f"Bearer {token}"}
        resp = client.post(
            "/workflow/routing",
            json={
                "name": "Route billing",
                "conditions": {"product_area": "billing"},
                "actions": {"set_priority": "high"},
            },
            headers=headers,
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["name"] == "Route billing"
        assert data["enabled"] is True

    def test_update_rule(self, client: TestClient):
        token, ws_id = _setup(client)
        headers = {"Authorization": f"Bearer {token}"}
        create = client.post(
            "/workflow/routing",
            json={"name": "Test", "conditions": {}, "actions": {}},
            headers=headers,
        )
        rule_id = create.json()["id"]
        resp = client.put(
            f"/workflow/routing/{rule_id}",
            json={"enabled": False},
            headers=headers,
        )
        assert resp.status_code == 200
        assert resp.json()["enabled"] is False

    def test_delete_rule(self, client: TestClient):
        token, ws_id = _setup(client)
        headers = {"Authorization": f"Bearer {token}"}
        create = client.post(
            "/workflow/routing",
            json={"name": "To delete", "conditions": {}, "actions": {}},
            headers=headers,
        )
        rule_id = create.json()["id"]
        resp = client.delete(f"/workflow/routing/{rule_id}", headers=headers)
        assert resp.status_code == 200
        assert resp.json()["ok"] is True

    def test_delete_not_found(self, client: TestClient):
        token, ws_id = _setup(client)
        headers = {"Authorization": f"Bearer {token}"}
        fake = "00000000-0000-0000-0000-000000000000"
        resp = client.delete(f"/workflow/routing/{fake}", headers=headers)
        assert resp.status_code == 404


class TestCannedResponses:
    def test_list_empty(self, client: TestClient):
        token, ws_id = _setup(client)
        headers = {"Authorization": f"Bearer {token}"}
        resp = client.get("/workflow/canned-responses", headers=headers)
        assert resp.status_code == 200
        assert resp.json()["total"] == 0

    def test_create_response(self, client: TestClient):
        token, ws_id = _setup(client)
        headers = {"Authorization": f"Bearer {token}"}
        resp = client.post(
            "/workflow/canned-responses",
            json={
                "title": "Password Reset",
                "content": "To reset your password, click the link in the email.",
                "category": "account",
                "shortcut": "!reset",
            },
            headers=headers,
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["title"] == "Password Reset"
        assert data["usage_count"] == 0

    def test_use_response(self, client: TestClient):
        token, ws_id = _setup(client)
        headers = {"Authorization": f"Bearer {token}"}
        create = client.post(
            "/workflow/canned-responses",
            json={"title": "Test", "content": "Test content"},
            headers=headers,
        )
        rid = create.json()["id"]
        resp = client.post(f"/workflow/canned-responses/{rid}/use", headers=headers)
        assert resp.status_code == 200
        assert resp.json()["usage_count"] == 1

    def test_search(self, client: TestClient):
        token, ws_id = _setup(client)
        headers = {"Authorization": f"Bearer {token}"}
        client.post(
            "/workflow/canned-responses",
            json={"title": "Billing Help", "content": "Contact billing@example.com"},
            headers=headers,
        )
        resp = client.get(
            "/workflow/canned-responses/search?q=billing", headers=headers,
        )
        assert resp.status_code == 200
        assert resp.json()["total"] >= 1

    def test_delete_response(self, client: TestClient):
        token, ws_id = _setup(client)
        headers = {"Authorization": f"Bearer {token}"}
        create = client.post(
            "/workflow/canned-responses",
            json={"title": "Delete me", "content": "x"},
            headers=headers,
        )
        rid = create.json()["id"]
        resp = client.delete(f"/workflow/canned-responses/{rid}", headers=headers)
        assert resp.status_code == 200


class TestPortalArticles:
    def test_list_empty(self, client: TestClient):
        token, ws_id = _setup(client)
        headers = {"Authorization": f"Bearer {token}"}
        resp = client.get("/workflow/portal", headers=headers)
        assert resp.status_code == 200
        assert resp.json()["total"] == 0

    def test_create_article(self, client: TestClient):
        token, ws_id = _setup(client)
        headers = {"Authorization": f"Bearer {token}"}
        resp = client.post(
            "/workflow/portal",
            json={
                "title": "How to Reset Password",
                "content": "Step 1: Go to settings. Step 2: Click reset.",
                "category": "account",
                "tags": ["password", "account"],
                "published": True,
            },
            headers=headers,
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["title"] == "How to Reset Password"
        assert data["slug"] == "how-to-reset-password"
        assert data["published"] is True
        assert "password" in data["tags"]

    def test_update_article(self, client: TestClient):
        token, ws_id = _setup(client)
        headers = {"Authorization": f"Bearer {token}"}
        create = client.post(
            "/workflow/portal",
            json={"title": "Original", "content": "Original content"},
            headers=headers,
        )
        aid = create.json()["id"]
        resp = client.put(
            f"/workflow/portal/{aid}",
            json={"title": "Updated", "published": True},
            headers=headers,
        )
        assert resp.status_code == 200
        assert resp.json()["title"] == "Updated"
        assert resp.json()["published"] is True

    def test_search(self, client: TestClient):
        token, ws_id = _setup(client)
        headers = {"Authorization": f"Bearer {token}"}
        client.post(
            "/workflow/portal",
            json={
                "title": "Billing FAQ",
                "content": "How to check your bill",
                "tags": ["billing"],
                "published": True,
            },
            headers=headers,
        )
        resp = client.get("/workflow/portal/search?q=billing", headers=headers)
        assert resp.status_code == 200
        assert resp.json()["total"] >= 1

    def test_delete_article(self, client: TestClient):
        token, ws_id = _setup(client)
        headers = {"Authorization": f"Bearer {token}"}
        create = client.post(
            "/workflow/portal",
            json={"title": "Delete me", "content": "x"},
            headers=headers,
        )
        aid = create.json()["id"]
        resp = client.delete(f"/workflow/portal/{aid}", headers=headers)
        assert resp.status_code == 200


class TestTicketStatus:
    def test_ticket_not_found(self, client: TestClient):
        token, ws_id = _setup(client)
        headers = {"Authorization": f"Bearer {token}"}
        resp = client.get(
            "/workflow/portal/ticket-status?ticket_id=nonexistent",
            headers=headers,
        )
        assert resp.status_code == 404
