"""Tests for V7 tool registry, execution, and action logs API."""
import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.core.database import get_db
from tests.conftest import TestingSessionLocal, engine, Base


def _setup(client: TestClient) -> tuple[str, str]:
    """Register user, create workspace, return (token, workspace_id)."""
    resp = client.post(
        "/auth/register",
        json={"email": "tools-test@example.com", "password": "password123"},
    )
    token = resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    ws_resp = client.post("/workspaces", json={"name": "Tools Test WS"}, headers=headers)
    ws_id = ws_resp.json()["id"]
    return token, ws_id


class TestToolList:
    def test_list_tools_auto_registers_builtins(self, client: TestClient):
        token, ws_id = _setup(client)
        headers = {"Authorization": f"Bearer {token}"}
        resp = client.get("/tools", headers=headers)
        assert resp.status_code == 200
        data = resp.json()
        assert data["total"] >= 6
        slugs = [t["slug"] for t in data["items"]]
        assert "create_ticket" in slugs
        assert "lookup_customer" in slugs
        assert "search_knowledge_base" in slugs
        assert "check_sla_status" in slugs
        assert "update_ticket_status" in slugs
        assert "list_handoffs" in slugs

    def test_list_tools_idempotent(self, client: TestClient):
        token, ws_id = _setup(client)
        headers = {"Authorization": f"Bearer {token}"}
        client.get("/tools", headers=headers)
        resp = client.get("/tools", headers=headers)
        assert resp.status_code == 200
        assert resp.json()["total"] >= 6

    def test_list_tools_requires_auth(self, client: TestClient):
        resp = client.get("/tools")
        assert resp.status_code in (401, 403)


class TestToolDetail:
    def test_get_tool(self, client: TestClient):
        token, ws_id = _setup(client)
        headers = {"Authorization": f"Bearer {token}"}
        list_resp = client.get("/tools", headers=headers)
        tool_id = list_resp.json()["items"][0]["id"]
        resp = client.get(f"/tools/{tool_id}", headers=headers)
        assert resp.status_code == 200
        assert resp.json()["id"] == tool_id
        assert "name" in resp.json()
        assert "parameters_schema" in resp.json()

    def test_get_tool_not_found(self, client: TestClient):
        token, ws_id = _setup(client)
        headers = {"Authorization": f"Bearer {token}"}
        fake_id = "00000000-0000-0000-0000-000000000000"
        resp = client.get(f"/tools/{fake_id}", headers=headers)
        assert resp.status_code == 404


class TestToolUpdate:
    def test_disable_tool(self, client: TestClient):
        token, ws_id = _setup(client)
        headers = {"Authorization": f"Bearer {token}"}
        list_resp = client.get("/tools", headers=headers)
        tool_id = list_resp.json()["items"][0]["id"]
        resp = client.put(
            f"/tools/{tool_id}",
            json={"enabled": False},
            headers=headers,
        )
        assert resp.status_code == 200
        assert resp.json()["enabled"] is False

    def test_enable_tool(self, client: TestClient):
        token, ws_id = _setup(client)
        headers = {"Authorization": f"Bearer {token}"}
        list_resp = client.get("/tools", headers=headers)
        tool_id = list_resp.json()["items"][0]["id"]
        client.put(f"/tools/{tool_id}", json={"enabled": False}, headers=headers)
        resp = client.put(f"/tools/{tool_id}", json={"enabled": True}, headers=headers)
        assert resp.status_code == 200
        assert resp.json()["enabled"] is True


class TestToolExecution:
    def test_execute_create_ticket(self, client: TestClient):
        token, ws_id = _setup(client)
        headers = {"Authorization": f"Bearer {token}"}
        list_resp = client.get("/tools", headers=headers)
        tool = next(
            t for t in list_resp.json()["items"] if t["slug"] == "create_ticket"
        )
        resp = client.post(
            f"/tools/{tool['id']}/execute",
            json={"parameters": {"title": "Test Bug", "body": "App crashes on login"}},
            headers=headers,
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "succeeded"
        assert data["tool_name"] == "Create Ticket"
        assert "ticket_id" in data["output"]
        assert data["latency_ms"] is not None

    def test_execute_disabled_tool_fails(self, client: TestClient):
        token, ws_id = _setup(client)
        headers = {"Authorization": f"Bearer {token}"}
        list_resp = client.get("/tools", headers=headers)
        tool = list_resp.json()["items"][0]
        client.put(f"/tools/{tool['id']}", json={"enabled": False}, headers=headers)
        resp = client.post(
            f"/tools/{tool['id']}/execute",
            json={"parameters": {}},
            headers=headers,
        )
        assert resp.status_code == 400
        assert "disabled" in resp.json()["detail"]

    def test_execute_tool_not_found(self, client: TestClient):
        token, ws_id = _setup(client)
        headers = {"Authorization": f"Bearer {token}"}
        fake_id = "00000000-0000-0000-0000-000000000000"
        resp = client.post(
            f"/tools/{fake_id}/execute",
            json={"parameters": {}},
            headers=headers,
        )
        assert resp.status_code == 404

    def test_execute_search_kb(self, client: TestClient):
        token, ws_id = _setup(client)
        headers = {"Authorization": f"Bearer {token}"}
        list_resp = client.get("/tools", headers=headers)
        tool = next(
            t for t in list_resp.json()["items"] if t["slug"] == "search_knowledge_base"
        )
        resp = client.post(
            f"/tools/{tool['id']}/execute",
            json={"parameters": {"query": "login issue"}},
            headers=headers,
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "succeeded"
        assert "articles" in data["output"]

    def test_execute_lookup_customer(self, client: TestClient):
        token, ws_id = _setup(client)
        headers = {"Authorization": f"Bearer {token}"}
        list_resp = client.get("/tools", headers=headers)
        tool = next(
            t for t in list_resp.json()["items"] if t["slug"] == "lookup_customer"
        )
        resp = client.post(
            f"/tools/{tool['id']}/execute",
            json={"parameters": {"email": "nobody@example.com"}},
            headers=headers,
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "succeeded"
        assert "customers" in data["output"]


class TestToolExecutionsList:
    def test_list_executions(self, client: TestClient):
        token, ws_id = _setup(client)
        headers = {"Authorization": f"Bearer {token}"}
        # Execute a tool first
        list_resp = client.get("/tools", headers=headers)
        tool = next(
            t for t in list_resp.json()["items"] if t["slug"] == "create_ticket"
        )
        client.post(
            f"/tools/{tool['id']}/execute",
            json={"parameters": {"title": "Test", "body": "Test"}},
            headers=headers,
        )
        resp = client.get("/tools/executions", headers=headers)
        assert resp.status_code == 200
        assert resp.json()["total"] >= 1
        item = resp.json()["items"][0]
        assert "tool_name" in item
        assert "status" in item


class TestActionLogs:
    def test_list_action_logs(self, client: TestClient):
        token, ws_id = _setup(client)
        headers = {"Authorization": f"Bearer {token}"}
        # Execute a tool to generate an action log
        list_resp = client.get("/tools", headers=headers)
        tool = next(
            t for t in list_resp.json()["items"] if t["slug"] == "create_ticket"
        )
        client.post(
            f"/tools/{tool['id']}/execute",
            json={"parameters": {"title": "Test", "body": "Test"}},
            headers=headers,
        )
        resp = client.get("/tools/action-logs", headers=headers)
        assert resp.status_code == 200
        assert resp.json()["total"] >= 1
        log = resp.json()["items"][0]
        assert log["action_type"] == "tool.create_ticket"
        assert log["actor"] in ("ai_agent", "user")


class TestWidgetAutoTool:
    def test_widget_chat_with_ticket_intent(self, client: TestClient):
        """Widget chat auto-creates a ticket when message matches intent."""
        token, ws_id = _setup(client)
        headers = {"Authorization": f"Bearer {token}"}

        # Start a widget session
        resp = client.post(
            "/widget/session",
            json={
                "customer_email": "auto@example.com",
                "customer_name": "Auto Test",
                "workspace_id": ws_id,
            },
            headers={"X-Widget-Key": "dev-widget-key"},
        )
        conv_id = resp.json()["conversation_id"]

        # Send a message that triggers ticket creation
        resp = client.post(
            "/widget/chat",
            json={
                "message": "I need to create a ticket for a login bug",
                "conversation_id": conv_id,
                "customer_email": "auto@example.com",
                "workspace_id": ws_id,
            },
            headers={"X-Widget-Key": "dev-widget-key"},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert "tool_results" in data
        assert len(data["tool_results"]) >= 1
        assert data["tool_results"][0]["tool_slug"] == "create_ticket"
        assert data["tool_results"][0]["status"] == "succeeded"
