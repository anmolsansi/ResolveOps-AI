"""Tests for V8 intelligence and feedback loop."""
from fastapi.testclient import TestClient


def _setup(client: TestClient) -> tuple[str, str]:
    """Register user, create workspace, return (token, workspace_id)."""
    resp = client.post(
        "/auth/register",
        json={"email": "intel-test@example.com", "password": "password123"},
    )
    token = resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    ws_resp = client.post("/workspaces", json={"name": "Intel Test WS"}, headers=headers)
    ws_id = ws_resp.json()["id"]
    return token, ws_id


class TestPerformanceMetrics:
    def test_performance_empty(self, client: TestClient):
        token, ws_id = _setup(client)
        headers = {"Authorization": f"Bearer {token}"}
        resp = client.get("/intelligence/performance", headers=headers)
        assert resp.status_code == 200
        data = resp.json()
        assert data["total_conversations"] == 0
        assert data["resolved_conversations"] == 0
        assert data["containment_rate"] == 0.0
        assert data["total_tool_executions"] == 0

    def test_performance_requires_auth(self, client: TestClient):
        resp = client.get("/intelligence/performance")
        assert resp.status_code in (401, 403)


class TestKbSuggestions:
    def test_detect_empty(self, client: TestClient):
        token, ws_id = _setup(client)
        headers = {"Authorization": f"Bearer {token}"}
        resp = client.post("/intelligence/kb-suggestions/detect", headers=headers)
        assert resp.status_code == 200
        assert resp.json()["total"] == 0

    def test_list_empty(self, client: TestClient):
        token, ws_id = _setup(client)
        headers = {"Authorization": f"Bearer {token}"}
        resp = client.get("/intelligence/kb-suggestions", headers=headers)
        assert resp.status_code == 200
        assert resp.json()["total"] == 0


class TestCopilot:
    def test_generate_copilot(self, client: TestClient):
        token, ws_id = _setup(client)
        headers = {"Authorization": f"Bearer {token}"}
        resp = client.post("/intelligence/copilot/generate", headers=headers)
        assert resp.status_code == 200
        data = resp.json()
        assert "items" in data

    def test_list_copilot(self, client: TestClient):
        token, ws_id = _setup(client)
        headers = {"Authorization": f"Bearer {token}"}
        resp = client.get("/intelligence/copilot", headers=headers)
        assert resp.status_code == 200
        assert resp.json()["total"] == 0


class TestSummaries:
    def test_list_empty(self, client: TestClient):
        token, ws_id = _setup(client)
        headers = {"Authorization": f"Bearer {token}"}
        resp = client.get("/intelligence/summaries", headers=headers)
        assert resp.status_code == 200
        assert resp.json()["total"] == 0


class TestFeedbackSummary:
    def test_feedback_empty(self, client: TestClient):
        token, ws_id = _setup(client)
        headers = {"Authorization": f"Bearer {token}"}
        resp = client.get("/intelligence/feedback-summary", headers=headers)
        assert resp.status_code == 200
        data = resp.json()
        assert data["total_feedback"] == 0
        assert data["satisfaction_rate"] == 0.0
        assert isinstance(data["improvement_areas"], list)


class TestIntelligenceWithV6Data:
    """Test intelligence metrics with actual conversation/tool data."""

    def _create_conversation_with_data(self, client, token, ws_id):
        headers = {"Authorization": f"Bearer {token}"}
        # Create a widget session
        ws_resp = client.post(
            "/widget/session",
            json={
                "customer_email": "intel-user@example.com",
                "customer_name": "Intel User",
                "workspace_id": ws_id,
            },
            headers={"X-Widget-Key": "dev-widget-key"},
        )
        conv_id = ws_resp.json()["conversation_id"]

        # Send a few messages
        for msg in ["How do I reset my password?", "I need billing help"]:
            client.post(
                "/widget/chat",
                json={
                    "message": msg,
                    "conversation_id": conv_id,
                    "customer_email": "intel-user@example.com",
                    "workspace_id": ws_id,
                },
                headers={"X-Widget-Key": "dev-widget-key"},
            )

        # Execute a tool
        tools_resp = client.get("/tools", headers=headers)
        create_tool = next(
            (t for t in tools_resp.json()["items"] if t["slug"] == "create_ticket"),
            None,
        )
        if create_tool:
            client.post(
                f"/tools/{create_tool['id']}/execute",
                json={"parameters": {"title": "Test", "body": "Test"}},
                headers=headers,
            )

        return conv_id

    def test_performance_with_data(self, client: TestClient):
        token, ws_id = _setup(client)
        self._create_conversation_with_data(client, token, ws_id)
        headers = {"Authorization": f"Bearer {token}"}
        resp = client.get("/intelligence/performance", headers=headers)
        assert resp.status_code == 200
        data = resp.json()
        assert data["total_conversations"] >= 1
        assert data["total_tool_executions"] >= 1

    def test_feedback_with_data(self, client: TestClient):
        token, ws_id = _setup(client)
        self._create_conversation_with_data(client, token, ws_id)
        headers = {"Authorization": f"Bearer {token}"}
        resp = client.get("/intelligence/feedback-summary", headers=headers)
        assert resp.status_code == 200
        assert resp.json()["total_feedback"] >= 0

    def test_copilot_with_pending_handoffs(self, client: TestClient):
        token, ws_id = _setup(client)
        headers = {"Authorization": f"Bearer {token}"}
        # Trigger a handoff via widget (angry message)
        ws_resp = client.post(
            "/widget/session",
            json={
                "customer_email": "angry@example.com",
                "customer_name": "Angry User",
                "workspace_id": ws_id,
            },
            headers={"X-Widget-Key": "dev-widget-key"},
        )
        conv_id = ws_resp.json()["conversation_id"]
        client.post(
            "/widget/chat",
            json={
                "message": "This is terrible and unacceptable! I'm furious!",
                "conversation_id": conv_id,
                "customer_email": "angry@example.com",
                "workspace_id": ws_id,
            },
            headers={"X-Widget-Key": "dev-widget-key"},
        )

        # Generate copilot suggestions
        resp = client.post("/intelligence/copilot/generate", headers=headers)
        assert resp.status_code == 200
        items = resp.json()["items"]
        types = [i["suggestion_type"] for i in items]
        assert "next_best_action" in types
