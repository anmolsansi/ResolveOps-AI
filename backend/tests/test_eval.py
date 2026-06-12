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


def _upload(client, rows, headers=None):
    csv_file = _make_csv(rows)
    return client.post(
        "/tickets/upload",
        files={"file": ("tickets.csv", csv_file, "text/csv")},
        headers=headers,
    )


ROWS = [
    {
        "id": f"T-{i}",
        "title": f"Issue {i} about billing",
        "body": f"Detailed billing problem description {i}",
        "product_area": "Billing",
        "issue_type": "Bug",
        "priority": "High",
        "customer_tier": "Enterprise",
        "status": "Resolved",
        "resolution": f"Billing issue {i} was resolved by refund",
        "created_at": f"2025-01-{10 + i:02d}",
        "resolved_at": f"2025-01-{11 + i:02d}",
    }
    for i in range(5)
]


def test_eval_run_default_questions(client, auth_headers):
    _upload(client, ROWS, auth_headers)
    resp = client.post("/eval/run", json={}, headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["total_questions"] == 5
    assert data["passed_count"] + data["failed_count"] == 5


def test_eval_run_custom_questions(client, auth_headers):
    _upload(client, ROWS, auth_headers)
    resp = client.post(
        "/eval/run",
        json={
            "name": "custom-eval",
            "questions": [
                {"question": "How to fix billing?"},
                {"question": "Something completely unrelated to anything"},
            ],
        },
        headers=auth_headers,
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["name"] == "custom-eval"
    assert data["total_questions"] == 2


def test_eval_list_runs(client, auth_headers):
    _upload(client, ROWS, auth_headers)
    client.post("/eval/run", json={"name": "run-1"}, headers=auth_headers)
    client.post("/eval/run", json={"name": "run-2"}, headers=auth_headers)
    resp = client.get("/eval/runs", headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) >= 2


def test_eval_empty_db(client, auth_headers):
    resp = client.post("/eval/run", json={}, headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["total_questions"] == 5
    assert data["failed_count"] == 5


def test_eval_run_has_average_confidence(client, auth_headers):
    _upload(client, ROWS, auth_headers)
    resp = client.post("/eval/run", json={}, headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert "average_confidence" in data
    assert isinstance(data["average_confidence"], float)


def test_eval_run_has_average_latency(client, auth_headers):
    _upload(client, ROWS, auth_headers)
    resp = client.post("/eval/run", json={}, headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert "average_latency_ms" in data
    assert data["average_latency_ms"] >= 0


def test_eval_run_has_results_json(client, auth_headers):
    _upload(client, ROWS, auth_headers)
    resp = client.post("/eval/run", json={}, headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert "results_json" in data
    assert data["results_json"] is not None
    import json
    results = json.loads(data["results_json"])
    assert len(results) == 5
    for result in results:
        assert "question" in result
        assert "passed" in result
        assert "confidence" in result


def test_eval_list_empty(client, auth_headers):
    resp = client.get("/eval/runs", headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data == []


def test_eval_run_records_rag_queries(client, auth_headers):
    _upload(client, ROWS, auth_headers)
    client.post("/eval/run", json={}, headers=auth_headers)
    resp = client.get("/dashboard/retrieval", headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["total_queries"] >= 5


def test_eval_requires_auth(client):
    resp = client.post("/eval/run", json={})
    assert resp.status_code == 401
