import io


def _make_csv(rows: list[dict]) -> io.BytesIO:
    cols = [
        "id", "title", "body", "product_area", "issue_type",
        "priority", "customer_tier", "status", "resolution",
        "created_at", "resolved_at",
    ]
    lines = [",".join(cols)]
    for row in rows:
        values = [str(row.get(c, "")) for c in cols]
        lines.append(",".join(values))
    return io.BytesIO("\n".join(lines).encode("utf-8"))


def _upload(client, rows):
    csv_file = _make_csv(rows)
    return client.post(
        "/tickets/upload",
        files={"file": ("tickets.csv", csv_file, "text/csv")},
    )


VALID_ROW = {
    "id": "T-1",
    "title": "Test",
    "body": "Test body",
    "product_area": "Auth",
    "issue_type": "Bug",
    "priority": "High",
    "customer_tier": "Enterprise",
    "status": "Open",
    "resolution": "Fixed",
    "created_at": "2025-01-15",
    "resolved_at": "",
}


def test_quality_empty(client):
    resp = client.get("/dashboard/quality")
    assert resp.status_code == 200
    data = resp.json()
    assert data["total_batches"] == 0
    assert data["total_rows_seen"] == 0
    assert data["valid_rate"] == 0.0
    assert data["invalid_rate"] == 0.0


def test_quality_after_upload(client):
    _upload(client, [VALID_ROW])
    resp = client.get("/dashboard/quality")
    assert resp.status_code == 200
    data = resp.json()
    assert data["total_batches"] == 1
    assert data["total_valid_rows"] == 1


def test_retrieval_empty(client):
    resp = client.get("/dashboard/retrieval")
    assert resp.status_code == 200
    data = resp.json()
    assert data["total_queries"] == 0
    assert data["average_confidence"] == 0.0
    assert data["average_latency_ms"] == 0
    assert data["total_estimated_cost_usd"] == 0.0


def test_retrieval_after_query(client):
    _upload(client, [VALID_ROW])
    client.post("/rag/query", json={"question": "Login problem"})
    resp = client.get("/dashboard/retrieval")
    assert resp.status_code == 200
    data = resp.json()
    assert data["total_queries"] >= 1


def test_quality_rates(client):
    rows = [
        VALID_ROW,
        {**VALID_ROW, "id": "T-2", "title": "Valid 2"},
        {**VALID_ROW, "id": "T-3", "title": ""},  # invalid
    ]
    _upload(client, rows)
    resp = client.get("/dashboard/quality")
    assert resp.status_code == 200
    data = resp.json()
    assert data["total_rows_seen"] == 3
    assert data["total_valid_rows"] == 2
    assert data["total_invalid_rows"] == 1
    assert data["valid_rate"] > 0
    assert data["invalid_rate"] > 0


def test_quality_duplicate_count(client):
    rows = [VALID_ROW, VALID_ROW]
    _upload(client, rows)
    resp = client.get("/dashboard/quality")
    assert resp.status_code == 200
    data = resp.json()
    assert data["total_duplicate_rows"] == 1


def test_quality_recent_batches(client):
    _upload(client, [VALID_ROW])
    _upload(client, [{**VALID_ROW, "id": "T-2"}])
    resp = client.get("/dashboard/quality")
    assert resp.status_code == 200
    data = resp.json()
    assert data["total_batches"] == 2
    assert len(data["recent_batches"]) == 2


def test_retrieval_recent_queries(client):
    _upload(client, [VALID_ROW])
    client.post("/rag/query", json={"question": "Q1"})
    client.post("/rag/query", json={"question": "Q2"})
    resp = client.get("/dashboard/retrieval")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data["recent_queries"]) >= 2


def test_retrieval_citation_rate(client):
    _upload(client, [VALID_ROW])
    client.post("/rag/query", json={"question": "test query"})
    resp = client.get("/dashboard/retrieval")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data["citation_rate"], float)
