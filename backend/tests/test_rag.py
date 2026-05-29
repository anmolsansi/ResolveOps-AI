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


ROWS = [
    {
        "id": f"T-{i}",
        "title": f"Billing error #{i}",
        "body": f"Customer was charged incorrectly for subscription plan {i}",
        "product_area": "Billing",
        "issue_type": "Bug",
        "priority": "High",
        "customer_tier": "Enterprise",
        "status": "Resolved",
        "resolution": f"Refund issued and billing corrected for case {i}",
        "created_at": f"2025-01-{10 + i:02d}",
        "resolved_at": f"2025-01-{11 + i:02d}",
    }
    for i in range(5)
]


def test_rag_query_with_data(client):
    _upload(client, ROWS)
    resp = client.post(
        "/rag/query",
        json={"question": "How to fix a billing error?"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert "answer" in data
    assert "citations" in data
    assert "confidence" in data
    assert "latency_ms" in data


def test_rag_query_empty_db(client):
    resp = client.post(
        "/rag/query",
        json={"question": "How to fix a billing error?"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert "enough context" in data["answer"].lower()


def test_rag_query_with_filters(client):
    _upload(client, ROWS)
    resp = client.post(
        "/rag/query",
        json={
            "question": "Billing problem",
            "filters": {"product_area": "Billing"},
        },
    )
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data["retrieved_chunks"], list)


def test_rag_query_low_confidence_fallback(client):
    resp = client.post(
        "/rag/query",
        json={"question": "What is quantum physics?"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert "enough context" in data["answer"].lower()
    assert data["confidence"] < 0.3
    assert data["citations"] == []


def test_rag_query_citations_structure(client):
    _upload(client, ROWS)
    resp = client.post(
        "/rag/query",
        json={"question": "billing error subscription refund"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["confidence"] >= 0.3
    assert len(data["citations"]) > 0
    for citation in data["citations"]:
        assert citation.startswith("T-")


def test_rag_query_returns_retrieved_chunks(client):
    _upload(client, ROWS)
    resp = client.post(
        "/rag/query",
        json={"question": "billing error", "top_k": 3},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert len(data["retrieved_chunks"]) <= 3
    for chunk in data["retrieved_chunks"]:
        assert "chunk_id" in chunk
        assert "ticket_id" in chunk
        assert "score" in chunk
        assert "preview" in chunk


def test_rag_query_logs_estimated_cost(client):
    _upload(client, ROWS)
    resp = client.post(
        "/rag/query",
        json={"question": "billing error"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert "estimated_cost_usd" in data
    assert data["estimated_cost_usd"] == 0.0  # mock provider


def test_rag_query_filter_no_match(client):
    _upload(client, ROWS)
    resp = client.post(
        "/rag/query",
        json={
            "question": "billing error",
            "filters": {"product_area": "Nonexistent"},
        },
    )
    assert resp.status_code == 200
    data = resp.json()
    assert "enough context" in data["answer"].lower()


def test_rag_query_records_in_db(client):
    _upload(client, ROWS)
    client.post("/rag/query", json={"question": "billing error"})
    resp = client.get("/dashboard/retrieval")
    assert resp.status_code == 200
    data = resp.json()
    assert data["total_queries"] >= 1


LOGIN_ROWS = [
    {
        "id": f"LOGIN-{i}",
        "title": "Login fails after password reset",
        "body": (
            "User cannot log in after resetting password. "
            "Login page shows invalid credentials error."
        ),
        "product_area": "Auth",
        "issue_type": "Bug",
        "priority": "High",
        "customer_tier": "Enterprise",
        "status": "Open",
        "resolution": "",
        "created_at": f"2025-01-{10 + i:02d}",
        "resolved_at": "",
    }
    for i in range(5)
]


def test_rag_related_query_returns_cited_answer(client):
    _upload(client, LOGIN_ROWS)
    resp = client.post(
        "/rag/query",
        json={"question": "How to fix login issues?"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert "enough context" not in data["answer"].lower()
    assert len(data["citations"]) > 0
    assert data["confidence"] >= 0.3
