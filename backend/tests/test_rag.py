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
