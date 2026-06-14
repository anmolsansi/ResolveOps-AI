"""Tests for the V6 conversations API endpoints."""
import pytest
from fastapi.testclient import TestClient


def _setup(client: TestClient) -> tuple[str, str]:
    """Register a user, create workspace, return (auth_token, workspace_id)."""
    resp = client.post(
        "/auth/register",
        json={"email": "conv-test@example.com", "password": "password123"},
    )
    token = resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    ws_resp = client.post("/workspaces", json={"name": "Conv Test WS"}, headers=headers)
    ws_id = ws_resp.json()["id"]
    return token, ws_id


def _auth_headers(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


def _create_conversation_via_widget(client: TestClient, ws_id: str) -> str:
    headers = {"X-Widget-Key": "dev-widget-key"}
    resp = client.post(
        "/widget/chat",
        json={"message": "I need help with my account", "customer_email": "conv@example.com", "workspace_id": ws_id},
        headers=headers,
    )
    return resp.json()["conversation_id"]


class TestListConversations:
    def test_list_empty(self, client: TestClient):
        token, ws_id = _setup(client)
        resp = client.get("/conversations", headers=_auth_headers(token))
        assert resp.status_code == 200
        data = resp.json()
        assert data["items"] == []
        assert data["total"] == 0

    def test_list_with_conversations(self, client: TestClient):
        token, ws_id = _setup(client)
        _create_conversation_via_widget(client, ws_id)
        resp = client.get("/conversations", headers=_auth_headers(token))
        assert resp.status_code == 200
        data = resp.json()
        assert data["total"] >= 1
        assert len(data["items"]) >= 1

    def test_list_filter_by_status(self, client: TestClient):
        token, ws_id = _setup(client)
        _create_conversation_via_widget(client, ws_id)
        resp = client.get("/conversations?status=open", headers=_auth_headers(token))
        assert resp.status_code == 200

    def test_list_requires_auth(self, client: TestClient):
        resp = client.get("/conversations")
        assert resp.status_code == 401


class TestConversationDetail:
    def test_get_detail(self, client: TestClient):
        token, ws_id = _setup(client)
        conv_id = _create_conversation_via_widget(client, ws_id)
        resp = client.get(f"/conversations/{conv_id}", headers=_auth_headers(token))
        assert resp.status_code == 200
        data = resp.json()
        assert data["id"] == conv_id
        assert data["channel"] == "widget"
        assert len(data["messages"]) >= 2
        assert data["customer"] is not None

    def test_get_detail_not_found(self, client: TestClient):
        token, ws_id = _setup(client)
        resp = client.get(
            "/conversations/00000000-0000-0000-0000-000000000000",
            headers=_auth_headers(token),
        )
        assert resp.status_code == 404


class TestAgentReply:
    def test_send_reply(self, client: TestClient):
        token, ws_id = _setup(client)
        conv_id = _create_conversation_via_widget(client, ws_id)
        resp = client.post(
            f"/conversations/{conv_id}/reply",
            json={"content": "Thanks for reaching out! Let me help."},
            headers=_auth_headers(token),
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["role"] == "agent"
        assert data["content"] == "Thanks for reaching out! Let me help."

    def test_reply_not_found(self, client: TestClient):
        token, ws_id = _setup(client)
        resp = client.post(
            "/conversations/00000000-0000-0000-0000-000000000000/reply",
            json={"content": "Hello"},
            headers=_auth_headers(token),
        )
        assert resp.status_code == 404


class TestUpdateStatus:
    def test_update_status(self, client: TestClient):
        token, ws_id = _setup(client)
        conv_id = _create_conversation_via_widget(client, ws_id)
        resp = client.put(
            f"/conversations/{conv_id}/status",
            json={"status": "escalated"},
            headers=_auth_headers(token),
        )
        assert resp.status_code == 200

        detail = client.get(f"/conversations/{conv_id}", headers=_auth_headers(token))
        assert detail.json()["status"] == "escalated"


class TestResolveConversation:
    def test_resolve(self, client: TestClient):
        token, ws_id = _setup(client)
        conv_id = _create_conversation_via_widget(client, ws_id)
        resp = client.post(
            f"/conversations/{conv_id}/resolve",
            json={"outcome": "ai_contained", "notes": "Resolved via AI"},
            headers=_auth_headers(token),
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["outcome"] == "ai_contained"
        assert data["total_messages"] >= 2

    def test_resolve_not_found(self, client: TestClient):
        token, ws_id = _setup(client)
        resp = client.post(
            "/conversations/00000000-0000-0000-0000-000000000000/resolve",
            json={"outcome": "ai_contained"},
            headers=_auth_headers(token),
        )
        assert resp.status_code == 404


class TestHandoffs:
    def test_list_handoffs_empty(self, client: TestClient):
        token, ws_id = _setup(client)
        resp = client.get("/conversations/handoffs", headers=_auth_headers(token))
        assert resp.status_code == 200
        data = resp.json()
        assert data["pending_count"] == 0
        assert data["items"] == []

    def test_angry_message_creates_handoff(self, client: TestClient):
        token, ws_id = _setup(client)
        headers = {"X-Widget-Key": "dev-widget-key"}
        client.post(
            "/widget/chat",
            json={"message": "This is absolutely terrible! I want a refund immediately!", "workspace_id": ws_id},
            headers=headers,
        )
        resp = client.get("/conversations/handoffs", headers=_auth_headers(token))
        assert resp.status_code == 200
        data = resp.json()
        assert data["pending_count"] >= 1

    def test_update_handoff(self, client: TestClient):
        token, ws_id = _setup(client)
        headers = {"X-Widget-Key": "dev-widget-key"}
        client.post(
            "/widget/chat",
            json={"message": "This is furious and unacceptable!", "workspace_id": ws_id},
            headers=headers,
        )
        handoffs_resp = client.get("/conversations/handoffs", headers=_auth_headers(token))
        items = handoffs_resp.json()["items"]
        if items:
            hid = items[0]["id"]
            resp = client.put(
                f"/conversations/handoffs/{hid}",
                json={"status": "acknowledged"},
                headers=_auth_headers(token),
            )
            assert resp.status_code == 200


class TestCustomers:
    def test_list_customers_empty(self, client: TestClient):
        token, ws_id = _setup(client)
        resp = client.get("/conversations/customers", headers=_auth_headers(token))
        assert resp.status_code == 200
        assert resp.json()["total"] == 0

    def test_list_customers_after_chat(self, client: TestClient):
        token, ws_id = _setup(client)
        headers = {"X-Widget-Key": "dev-widget-key"}
        client.post(
            "/widget/chat",
            json={"message": "Hello", "customer_email": "cust@test.com", "workspace_id": ws_id},
            headers=headers,
        )
        resp = client.get("/conversations/customers", headers=_auth_headers(token))
        assert resp.status_code == 200
        assert resp.json()["total"] >= 1

    def test_customer_profile(self, client: TestClient):
        token, ws_id = _setup(client)
        headers = {"X-Widget-Key": "dev-widget-key"}
        client.post(
            "/widget/chat",
            json={"message": "Help me", "customer_email": "profile@test.com", "workspace_id": ws_id},
            headers=headers,
        )
        list_resp = client.get("/conversations/customers", headers=_auth_headers(token))
        items = list_resp.json()["items"]
        if items:
            cid = items[0]["id"]
            resp = client.get(f"/conversations/customers/{cid}", headers=_auth_headers(token))
            assert resp.status_code == 200
            data = resp.json()
            assert "profile" in data
            assert "timeline" in data
