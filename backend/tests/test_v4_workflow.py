import io


def _make_csv(rows: list[dict]) -> io.BytesIO:
    cols = [
        "id", "title", "body", "product_area", "issue_type",
        "priority", "customer_tier", "status", "resolution",
        "created_at", "resolved_at",
    ]
    lines = [",".join(cols)]
    for row in rows:
        values = [str(row.get(c, "")).replace(",", " ") for c in cols]
        lines.append(",".join(values))
    return io.BytesIO("\n".join(lines).encode("utf-8"))


def _upload(client, rows, headers=None):
    return client.post(
        "/tickets/upload",
        files={"file": ("tickets.csv", _make_csv(rows), "text/csv")},
        headers=headers,
    )


LOGIN_ROWS = [
    {
        "id": f"LOGIN-{i}",
        "title": "Login fails after password reset",
        "body": "User cannot login after resetting their password credentials",
        "product_area": "Auth",
        "issue_type": "Bug",
        "priority": "High",
        "customer_tier": "Enterprise",
        "status": "Resolved",
        "resolution": "Cleared cached session tokens and reset password link",
        "created_at": f"2025-01-{10 + i:02d}",
        "resolved_at": f"2025-01-{11 + i:02d}",
    }
    for i in range(4)
]

OPEN_CRITICAL_ROW = [
    {
        "id": "CRIT-1",
        "title": "Production API outage",
        "body": "API is returning 500 errors for all customers right now",
        "product_area": "API",
        "issue_type": "Bug",
        "priority": "Critical",
        "customer_tier": "Enterprise",
        "status": "Open",
        "resolution": "",
        "created_at": "2025-02-01",
        "resolved_at": "",
    }
]


# ---------------- Connectors ----------------

def test_create_connector_rejects_unknown_provider(client, auth_headers):
    r = client.post("/connectors", json={"provider": "salesforce", "name": "SF"}, headers=auth_headers)
    assert r.status_code == 400


def test_connector_create_and_list(client, auth_headers):
    r = client.post("/connectors", json={"provider": "zendesk", "name": "Support ZD"}, headers=auth_headers)
    assert r.status_code == 200
    body = r.json()
    assert body["provider"] == "zendesk"
    assert body["cursor"] is None

    lst = client.get("/connectors", headers=auth_headers).json()
    assert len(lst["items"]) == 1


def test_connector_sync_imports_and_dedupes(client, auth_headers):
    cid = client.post("/connectors", json={"provider": "zendesk", "name": "ZD"}, headers=auth_headers).json()["id"]
    r = client.post(f"/connectors/{cid}/sync?limit=10", headers=auth_headers)
    assert r.status_code == 200
    res = r.json()
    assert res["imported"] == 6
    assert res["duplicate_semantic"] == 1
    assert res["cursor"] == "7"


def test_connector_incremental_sync(client, auth_headers):
    cid = client.post("/connectors", json={"provider": "freshdesk", "name": "FD"}, headers=auth_headers).json()["id"]
    first = client.post(f"/connectors/{cid}/sync?limit=3", headers=auth_headers).json()
    assert first["imported"] == 3
    assert first["cursor"] == "3"
    second = client.post(f"/connectors/{cid}/sync?limit=3", headers=auth_headers).json()
    assert second["imported"] == 3
    assert second["cursor"] == "6"
    third = client.post(f"/connectors/{cid}/sync?limit=3", headers=auth_headers).json()
    assert third["fetched"] == 1
    assert third["imported"] == 0
    assert third["duplicate_semantic"] == 1


def test_scheduled_job_run_due(client, auth_headers):
    cid = client.post("/connectors", json={"provider": "intercom", "name": "IC"}, headers=auth_headers).json()["id"]
    job = client.post(f"/connectors/{cid}/jobs", json={"interval_minutes": 30}, headers=auth_headers).json()
    assert job["interval_minutes"] == 30

    jobs = client.get("/connectors/jobs", headers=auth_headers).json()
    assert len(jobs["items"]) == 1

    run = client.post("/connectors/jobs/run-due?limit=10", headers=auth_headers).json()
    assert run["ran"] == 1
    assert run["results"][0]["imported"] == 6

    run2 = client.post("/connectors/jobs/run-due?limit=10", headers=auth_headers).json()
    assert run2["ran"] == 0


def test_duplicate_detection_endpoint(client, auth_headers):
    rows = [
        {
            "id": "DUP-A",
            "title": "Password reset not working",
            "body": "Customer cannot reset their password from the settings page",
            "product_area": "Auth",
            "issue_type": "Bug",
            "priority": "High",
            "customer_tier": "Pro",
            "status": "Open",
            "resolution": "",
            "created_at": "2025-01-10",
            "resolved_at": "",
        },
        {
            "id": "DUP-B",
            "title": "Password reset not working",
            "body": "Customer cannot reset their password from the settings page",
            "product_area": "Auth",
            "issue_type": "Bug",
            "priority": "High",
            "customer_tier": "Pro",
            "status": "Open",
            "resolution": "",
            "created_at": "2025-01-11",
            "resolved_at": "",
        },
    ]
    _upload(client, rows, auth_headers)
    r = client.get("/connectors/duplicates", headers=auth_headers)
    assert r.status_code == 200
    clusters = r.json()["clusters"]
    assert len(clusters) == 1
    assert set(clusters[0]["ticket_ids"]) == {"DUP-A", "DUP-B"}
    assert clusters[0]["max_similarity"] >= 0.92


# ---------------- Assist ----------------

def test_assist_related_query_drafts_answer(client, auth_headers):
    _upload(client, LOGIN_ROWS, auth_headers)
    r = client.post(
        "/assist/draft",
        json={
            "subject": "Login not working after password reset",
            "body": "I reset my password and now cannot log in",
            "customer_tier": "Enterprise",
        },
        headers=auth_headers,
    )
    assert r.status_code == 200
    data = r.json()
    assert data["recommendation"] in {"answer", "ask_clarification"}
    assert len(data["citations"]) > 0
    assert "Enterprise" in data["tier_guidance"]
    assert "Confidence" in data["internal_note"]


def test_assist_unrelated_query_routes_to_human(client, auth_headers):
    _upload(client, LOGIN_ROWS, auth_headers)
    r = client.post(
        "/assist/draft",
        json={"subject": "Best chocolate cake recipe", "body": "How much cocoa?"},
        headers=auth_headers,
    )
    data = r.json()
    assert data["recommendation"] == "route_to_human"
    assert data["citations"] == []


# ---------------- Knowledge base ----------------

def test_kb_generation(client, auth_headers):
    _upload(client, LOGIN_ROWS, auth_headers)
    r = client.post("/kb/generate", headers=auth_headers)
    assert r.status_code == 200
    body = r.json()
    assert body["generated"] >= 1
    article = body["items"][0]
    assert article["ticket_count"] >= 2
    assert article["resolution_steps"]
    assert len(article["source_ticket_ids"]) >= 2

    listed = client.get("/kb/articles", headers=auth_headers).json()
    assert len(listed["items"]) == body["generated"]


def test_kb_generation_is_idempotent(client, auth_headers):
    _upload(client, LOGIN_ROWS, auth_headers)
    first = client.post("/kb/generate", headers=auth_headers).json()["generated"]
    second = client.post("/kb/generate", headers=auth_headers).json()["generated"]
    assert first == second
    assert len(client.get("/kb/articles", headers=auth_headers).json()["items"]) == second


# ---------------- SLA ----------------

def test_sla_risk_detection(client, auth_headers):
    _upload(client, OPEN_CRITICAL_ROW, auth_headers)
    r = client.get("/sla/risks", headers=auth_headers)
    assert r.status_code == 200
    data = r.json()
    assert data["breached_count"] >= 1
    top = data["items"][0]
    assert top["ticket_id"] == "CRIT-1"
    assert top["breached"] is True
    assert top["risk_level"] == "high"


def test_sla_excludes_resolved_tickets(client, auth_headers):
    _upload(client, LOGIN_ROWS, auth_headers)
    data = client.get("/sla/risks", headers=auth_headers).json()
    assert data["items"] == []


def test_v4_requires_auth(client):
    resp = client.post("/connectors", json={"provider": "zendesk", "name": "ZD"})
    assert resp.status_code == 401
    resp = client.post("/assist/draft", json={"subject": "test", "body": "test"})
    assert resp.status_code == 401
    resp = client.post("/kb/generate")
    assert resp.status_code == 401
    resp = client.get("/sla/risks")
    assert resp.status_code == 401
