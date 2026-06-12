import io

from app.services.quality import compute_quality_metrics, percentile


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
    return client.post(
        "/tickets/upload",
        files={"file": ("tickets.csv", _make_csv(rows), "text/csv")},
        headers=headers,
    )


BILLING_ROWS = [
    {
        "id": f"BILL-{i}",
        "title": f"Billing charge error #{i}",
        "body": "Customer was charged twice for the subscription invoice payment",
        "product_area": "Billing",
        "issue_type": "Bug",
        "priority": "High",
        "customer_tier": "Enterprise",
        "status": "Resolved",
        "resolution": "Refund issued and duplicate invoice charge reversed",
        "created_at": f"2025-01-{10 + i:02d}",
        "resolved_at": f"2025-01-{11 + i:02d}",
    }
    for i in range(5)
]

LOGIN_ROWS = [
    {
        "id": f"LOGIN-{i}",
        "title": "Login fails after password reset",
        "body": "User cannot login after resetting their password credentials",
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


# --- quality service unit tests ---


def test_percentile_basic():
    values = [10.0, 20.0, 30.0, 40.0, 50.0]
    assert percentile(values, 50) == 30.0
    assert percentile([], 95) == 0.0
    assert percentile([7.0], 99) == 7.0
    assert percentile(values, 0) == 10.0
    assert percentile(values, 100) == 50.0


def test_quality_metrics_fallback_zeroed():
    q = compute_quality_metrics(
        "billing refund question",
        "I don't have enough context to answer this question.",
        [],
        [],
        is_fallback=True,
    )
    assert q["citation_coverage"] == 0.0
    assert q["hallucination_risk"] == 0.0
    assert q["answer_completeness"] == 0.0
    assert q["retrieval_precision"] == 0.0


def test_quality_metrics_grounded_answer():
    retrieved = [{"ticket_id": "T-1", "text": "billing refund issued to customer"}]
    q = compute_quality_metrics(
        "billing refund",
        "The billing refund was issued to the customer.",
        retrieved,
        ["T-1"],
        is_fallback=False,
    )
    assert q["retrieval_precision"] == 1.0
    assert q["citation_coverage"] > 0.0
    assert 0.0 <= q["hallucination_risk"] <= 1.0
    assert q["answer_completeness"] > 0.0


# --- RAG endpoint quality + feedback ---


def test_rag_response_includes_quality(client, auth_headers):
    _upload(client, BILLING_ROWS, auth_headers)
    resp = client.post("/rag/query", json={"question": "billing charge invoice refund"}, headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert "query_id" in data
    assert data["provider"] == "mock"
    assert data["model"] == "mock-answer-v1"
    assert data["product_area"] == "Billing"
    assert data["is_fallback"] is False
    q = data["quality"]
    for key in [
        "hallucination_risk", "citation_coverage",
        "retrieval_precision", "answer_completeness",
    ]:
        assert 0.0 <= q[key] <= 1.0


def test_feedback_updates_query(client, auth_headers):
    _upload(client, BILLING_ROWS, auth_headers)
    resp = client.post("/rag/query", json={"question": "billing charge invoice refund"}, headers=auth_headers)
    query_id = resp.json()["query_id"]

    fb = client.post(f"/rag/queries/{query_id}/feedback", json={"feedback": "wrong_citation"}, headers=auth_headers)
    assert fb.status_code == 200
    assert fb.json()["feedback"] == "wrong_citation"


def test_feedback_invalid_value_rejected(client, auth_headers):
    _upload(client, BILLING_ROWS, auth_headers)
    resp = client.post("/rag/query", json={"question": "billing charge invoice refund"}, headers=auth_headers)
    query_id = resp.json()["query_id"]
    bad = client.post(f"/rag/queries/{query_id}/feedback", json={"feedback": "amazing"}, headers=auth_headers)
    assert bad.status_code == 422


def test_feedback_unknown_query_404(client, auth_headers):
    resp = client.post(
        "/rag/queries/00000000-0000-0000-0000-000000000000/feedback",
        json={"feedback": "helpful"},
        headers=auth_headers,
    )
    assert resp.status_code == 404


# --- dashboard reliability endpoints ---


def test_retrieval_metrics_has_percentiles_and_quality(client, auth_headers):
    _upload(client, BILLING_ROWS, auth_headers)
    client.post("/rag/query", json={"question": "billing charge invoice refund"}, headers=auth_headers)
    resp = client.get("/dashboard/retrieval", headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()
    for key in [
        "latency_p50_ms", "latency_p95_ms", "latency_p99_ms",
        "average_hallucination_risk", "average_citation_coverage",
        "average_retrieval_precision", "average_answer_completeness",
    ]:
        assert key in data


def test_cost_endpoint_groups_by_model(client, auth_headers):
    _upload(client, BILLING_ROWS, auth_headers)
    client.post("/rag/query", json={"question": "billing charge invoice refund"}, headers=auth_headers)
    resp = client.get("/dashboard/cost", headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["total_queries"] >= 1
    assert len(data["by_model"]) >= 1
    entry = data["by_model"][0]
    assert entry["provider"] == "mock"
    assert entry["model"] == "mock-answer-v1"
    assert entry["query_count"] >= 1


def test_quality_by_area_endpoint(client, auth_headers):
    _upload(client, BILLING_ROWS, auth_headers)
    client.post("/rag/query", json={"question": "billing charge invoice refund"}, headers=auth_headers)
    resp = client.get("/dashboard/quality-by-area", headers=auth_headers)
    assert resp.status_code == 200
    areas = resp.json()["areas"]
    assert any(a["product_area"] == "Billing" for a in areas)


def test_failed_queries_queue(client, auth_headers):
    _upload(client, BILLING_ROWS, auth_headers)
    client.post("/rag/query", json={"question": "chocolate cake recipe"}, headers=auth_headers)
    resp = client.get("/dashboard/failed-queries", headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["count"] >= 1
    assert any(item["reason"] == "low_confidence" for item in data["items"])


def test_failed_queries_includes_negative_feedback(client, auth_headers):
    _upload(client, BILLING_ROWS, auth_headers)
    resp = client.post("/rag/query", json={"question": "billing charge invoice refund"}, headers=auth_headers)
    query_id = resp.json()["query_id"]
    client.post(f"/rag/queries/{query_id}/feedback", json={"feedback": "not_helpful"}, headers=auth_headers)
    failed = client.get("/dashboard/failed-queries", headers=auth_headers).json()
    assert any(item["reason"] == "feedback:not_helpful" for item in failed["items"])


# --- eval regression compare ---


def test_eval_compare_returns_deltas(client, auth_headers):
    _upload(client, BILLING_ROWS, auth_headers)
    resp = client.post(
        "/eval/compare",
        json={
            "name": "topk-sweep",
            "questions": [{"question": "billing charge invoice refund"}],
            "config_a": {"label": "k1", "top_k": 1, "threshold": 0.3},
            "config_b": {"label": "k5", "top_k": 5, "threshold": 0.3},
        },
        headers=auth_headers,
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["config_a"]["label"] == "k1"
    assert data["config_b"]["label"] == "k5"
    assert data["total_questions"] == 1
    assert len(data["per_question"]) == 1
    assert "confidence_delta" in data
    assert "passed_delta" in data


def test_eval_compare_does_not_pollute_query_log(client, auth_headers):
    _upload(client, BILLING_ROWS, auth_headers)
    before = client.get("/dashboard/retrieval", headers=auth_headers).json()["total_queries"]
    client.post(
        "/eval/compare",
        json={
            "questions": [{"question": "billing charge invoice refund"}],
            "config_a": {"label": "a", "top_k": 3, "threshold": 0.3},
            "config_b": {"label": "b", "top_k": 5, "threshold": 0.5},
        },
        headers=auth_headers,
    )
    after = client.get("/dashboard/retrieval", headers=auth_headers).json()["total_queries"]
    assert after == before


def test_reliability_requires_auth(client):
    resp = client.post("/rag/query", json={"question": "test"})
    assert resp.status_code == 401
    resp = client.get("/dashboard/retrieval")
    assert resp.status_code == 401
    resp = client.get("/dashboard/failed-queries")
    assert resp.status_code == 401
