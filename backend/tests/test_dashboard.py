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


def test_quality_empty(client):
    resp = client.get("/dashboard/quality")
    assert resp.status_code == 200
    data = resp.json()
    assert data["total_batches"] == 0
    assert data["total_rows_seen"] == 0


def test_quality_after_upload(client):
    rows = [
        {
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
    ]
    _upload(client, rows)
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


def test_retrieval_after_query(client):
    rows = [
        {
            "id": "T-1",
            "title": "Login issue",
            "body": "Cannot login with valid password",
            "product_area": "Auth",
            "issue_type": "Bug",
            "priority": "High",
            "customer_tier": "Enterprise",
            "status": "Open",
            "resolution": "Reset password",
            "created_at": "2025-01-15",
            "resolved_at": "",
        }
    ]
    _upload(client, rows)
    client.post("/rag/query", json={"question": "Login problem"})
    resp = client.get("/dashboard/retrieval")
    assert resp.status_code == 200
    data = resp.json()
    assert data["total_queries"] >= 1
