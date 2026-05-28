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


def test_eval_run_default_questions(client):
    _upload(client, ROWS)
    resp = client.post("/eval/run", json={})
    assert resp.status_code == 200
    data = resp.json()
    assert data["total_questions"] == 5
    assert data["passed_count"] + data["failed_count"] == 5


def test_eval_run_custom_questions(client):
    _upload(client, ROWS)
    resp = client.post(
        "/eval/run",
        json={
            "name": "custom-eval",
            "questions": [
                {"question": "How to fix billing?"},
                {"question": "Something completely unrelated to anything"},
            ],
        },
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["name"] == "custom-eval"
    assert data["total_questions"] == 2


def test_eval_list_runs(client):
    _upload(client, ROWS)
    client.post("/eval/run", json={"name": "run-1"})
    client.post("/eval/run", json={"name": "run-2"})
    resp = client.get("/eval/runs")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) >= 2


def test_eval_empty_db(client):
    resp = client.post("/eval/run", json={})
    assert resp.status_code == 200
    data = resp.json()
    assert data["total_questions"] == 5
    assert data["failed_count"] == 5
