"""Tests for the V6 widget API endpoints."""
import pytest
from fastapi.testclient import TestClient


WIDGET_HEADERS = {"X-Widget-Key": "dev-widget-key"}
BAD_KEY_HEADERS = {"X-Widget-Key": "wrong-key"}


def _setup_workspace(client: TestClient) -> tuple[str, str]:
    """Register a user, trigger workspace creation, return (auth_token, workspace_id)."""
    resp = client.post(
        "/auth/register",
        json={"email": "ws-widget@example.com", "password": "password123"},
    )
    token = resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    # Create workspace explicitly
    ws_resp = client.post("/workspaces", json={"name": "Widget Test WS"}, headers=headers)
    ws_id = ws_resp.json()["id"]
    return token, ws_id


class TestWidgetHealth:
    def test_health_returns_ok(self, client: TestClient):
        resp = client.get("/widget/health")
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "ok"
        assert data["version"] == "v6"


class TestWidgetSession:
    def test_start_session_creates_conversation(self, client: TestClient):
        token, ws_id = _setup_workspace(client)
        resp = client.post(
            "/widget/session",
            json={"customer_email": "test@example.com", "customer_name": "Test User", "workspace_id": ws_id},
            headers=WIDGET_HEADERS,
        )
        assert resp.status_code == 200
        data = resp.json()
        assert "conversation_id" in data
        assert data["status"] == "open"

    def test_start_session_without_auth(self, client: TestClient):
        resp = client.post("/widget/session", json={})
        assert resp.status_code == 401

    def test_start_session_bad_key(self, client: TestClient):
        resp = client.post("/widget/session", json={}, headers=BAD_KEY_HEADERS)
        assert resp.status_code == 401


class TestWidgetChat:
    def test_chat_basic(self, client: TestClient):
        token, ws_id = _setup_workspace(client)
        resp = client.post(
            "/widget/chat",
            json={"message": "How do I reset my password?", "workspace_id": ws_id},
            headers=WIDGET_HEADERS,
        )
        assert resp.status_code == 200
        data = resp.json()
        assert "answer" in data
        assert "conversation_id" in data
        assert "message_id" in data
        assert isinstance(data["citations"], list)
        assert isinstance(data["confidence"], float)
        assert isinstance(data["is_fallback"], bool)
        assert data["sentiment"] in ("positive", "neutral", "negative", "angry")

    def test_chat_with_session(self, client: TestClient):
        token, ws_id = _setup_workspace(client)
        session_resp = client.post(
            "/widget/session",
            json={"customer_email": "user@test.com", "workspace_id": ws_id},
            headers=WIDGET_HEADERS,
        )
        conv_id = session_resp.json()["conversation_id"]

        resp = client.post(
            "/widget/chat",
            json={"message": "I need help with billing", "conversation_id": conv_id, "workspace_id": ws_id},
            headers=WIDGET_HEADERS,
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["conversation_id"] == conv_id

    def test_chat_empty_message(self, client: TestClient):
        token, ws_id = _setup_workspace(client)
        resp = client.post(
            "/widget/chat",
            json={"message": "   ", "workspace_id": ws_id},
            headers=WIDGET_HEADERS,
        )
        assert resp.status_code == 400

    def test_chat_creates_customer(self, client: TestClient):
        token, ws_id = _setup_workspace(client)
        resp = client.post(
            "/widget/chat",
            json={"message": "Hello", "customer_email": "new@example.com", "customer_name": "New User", "workspace_id": ws_id},
            headers=WIDGET_HEADERS,
        )
        assert resp.status_code == 200

        customer_resp = client.get(
            "/conversations/customers",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert customer_resp.status_code == 200
        customers = customer_resp.json()["items"]
        assert any(c["email"] == "new@example.com" for c in customers)

    def test_chat_angry_sentiment_triggers_escalation(self, client: TestClient):
        token, ws_id = _setup_workspace(client)
        resp = client.post(
            "/widget/chat",
            json={"message": "This is absolutely terrible and unacceptable! I am furious!", "workspace_id": ws_id},
            headers=WIDGET_HEADERS,
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["should_escalate"] is True
        assert data["sentiment"] == "angry"

    def test_chat_without_auth(self, client: TestClient):
        resp = client.post("/widget/chat", json={"message": "hello"})
        assert resp.status_code == 401


class TestWidgetFeedback:
    def test_submit_feedback(self, client: TestClient):
        token, ws_id = _setup_workspace(client)
        chat_resp = client.post(
            "/widget/chat",
            json={"message": "How do I login?", "workspace_id": ws_id},
            headers=WIDGET_HEADERS,
        )
        msg_id = chat_resp.json()["message_id"]

        resp = client.post(
            "/widget/feedback",
            json={"message_id": msg_id, "feedback": "helpful"},
            headers=WIDGET_HEADERS,
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["feedback"] == "helpful"

    def test_feedback_nonexistent_message(self, client: TestClient):
        resp = client.post(
            "/widget/feedback",
            json={"message_id": "00000000-0000-0000-0000-000000000000", "feedback": "helpful"},
            headers=WIDGET_HEADERS,
        )
        assert resp.status_code == 404
