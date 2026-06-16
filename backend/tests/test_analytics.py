"""Tests for V10a analytics and reporting."""
from fastapi.testclient import TestClient


def _setup(client: TestClient) -> tuple[str, str]:
    resp = client.post(
        "/auth/register",
        json={"email": "analytics-test@example.com", "password": "password123"},
    )
    token = resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    ws_resp = client.post("/workspaces", json={"name": "Analytics Test WS"}, headers=headers)
    ws_id = ws_resp.json()["id"]
    return token, ws_id


class TestDashboard:
    def test_dashboard_all_time(self, client: TestClient):
        token, _ = _setup(client)
        headers = {"Authorization": f"Bearer {token}"}
        resp = client.get("/analytics/dashboard?time_range=all", headers=headers)
        assert resp.status_code == 200
        data = resp.json()
        assert "total_conversations" in data
        assert "containment_rate" in data
        assert "trend" in data

    def test_dashboard_7d(self, client: TestClient):
        token, _ = _setup(client)
        headers = {"Authorization": f"Bearer {token}"}
        resp = client.get("/analytics/dashboard?time_range=7d", headers=headers)
        assert resp.status_code == 200

    def test_agent_performance(self, client: TestClient):
        token, _ = _setup(client)
        headers = {"Authorization": f"Bearer {token}"}
        resp = client.get("/analytics/agent-performance", headers=headers)
        assert resp.status_code == 200
        assert "items" in resp.json()

    def test_trends(self, client: TestClient):
        token, _ = _setup(client)
        headers = {"Authorization": f"Bearer {token}"}
        resp = client.get("/analytics/trends?metric=conversations&time_range=30d", headers=headers)
        assert resp.status_code == 200
        assert "data_points" in resp.json()


class TestSavedReports:
    def test_create_report(self, client: TestClient):
        token, _ = _setup(client)
        headers = {"Authorization": f"Bearer {token}"}
        resp = client.post(
            "/analytics/reports",
            json={
                "name": "Weekly Quality", "report_type": "quality",
                "filters": {"time_range": "7d"},
            },
            headers=headers,
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["name"] == "Weekly Quality"
        assert data["report_type"] == "quality"

    def test_list_reports(self, client: TestClient):
        token, _ = _setup(client)
        headers = {"Authorization": f"Bearer {token}"}
        client.post(
            "/analytics/reports",
            json={"name": "Test", "report_type": "retrieval"},
            headers=headers,
        )
        resp = client.get("/analytics/reports", headers=headers)
        assert resp.status_code == 200
        assert resp.json()["total"] >= 1

    def test_delete_report(self, client: TestClient):
        token, _ = _setup(client)
        headers = {"Authorization": f"Bearer {token}"}
        create = client.post(
            "/analytics/reports",
            json={"name": "Delete me", "report_type": "cost"},
            headers=headers,
        )
        rid = create.json()["id"]
        resp = client.delete(f"/analytics/reports/{rid}", headers=headers)
        assert resp.status_code == 200


class TestExports:
    def test_create_export(self, client: TestClient):
        token, _ = _setup(client)
        headers = {"Authorization": f"Bearer {token}"}
        resp = client.post(
            "/analytics/export",
            json={"report_type": "quality", "filters": {"time_range": "30d"}},
            headers=headers,
        )
        assert resp.status_code == 200
        assert resp.json()["status"] == "succeeded"

    def test_list_exports(self, client: TestClient):
        token, _ = _setup(client)
        headers = {"Authorization": f"Bearer {token}"}
        client.post(
            "/analytics/export",
            json={"report_type": "quality"},
            headers=headers,
        )
        resp = client.get("/analytics/exports", headers=headers)
        assert resp.status_code == 200
        assert resp.json()["total"] >= 1

    def test_download_export(self, client: TestClient):
        token, _ = _setup(client)
        headers = {"Authorization": f"Bearer {token}"}
        create = client.post(
            "/analytics/export",
            json={"report_type": "quality"},
            headers=headers,
        )
        eid = create.json()["id"]
        resp = client.get(f"/analytics/exports/{eid}/download", headers=headers)
        assert resp.status_code == 200
        assert "text/csv" in resp.headers["content-type"]
