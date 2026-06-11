from datetime import datetime

from app.models.models import Ticket, TicketChunk


def _admin_headers(client):
    token = client.post(
        "/auth/register", json={"email": "owner@example.com", "password": "password123"}
    ).json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def _make_ticket(db, tid="TK-1", body="login fails", title="Login issue"):
    ticket = Ticket(
        id=tid,
        title=title,
        body=body,
        product_area="Authentication",
        issue_type="Bug",
        priority="High",
        customer_tier="Enterprise",
        status="Open",
        resolution="",
        created_at=datetime.utcnow(),
    )
    db.add(ticket)
    db.flush()
    return ticket


def test_enqueue_unknown_job_type_422(client):
    headers = _admin_headers(client)
    resp = client.post("/jobs", json={"job_type": "nope"}, headers=headers)
    assert resp.status_code == 422


def test_enqueue_requires_auth(client):
    resp = client.post("/jobs", json={"job_type": "retention_run"})
    assert resp.status_code == 401


def test_embedding_backfill_job(client, db_session):
    headers = _admin_headers(client)
    ticket = _make_ticket(db_session)
    db_session.add(
        TicketChunk(ticket_id=ticket.id, chunk_index=0, text="login fails", embedding=None)
    )
    db_session.commit()

    job = client.post("/jobs", json={"job_type": "embedding_backfill"}, headers=headers).json()
    assert job["status"] == "pending"

    result = client.post("/jobs/process-pending", headers=headers).json()
    assert result["processed"] == 1
    assert result["succeeded"] == 1
    assert result["jobs"][0]["status"] == "succeeded"

    # the chunk now has an embedding
    chunk = db_session.query(TicketChunk).first()
    db_session.refresh(chunk)
    assert chunk.embedding is not None


def test_retention_run_job(client, db_session):
    headers = _admin_headers(client)
    job = client.post("/jobs", json={"job_type": "retention_run"}, headers=headers).json()
    result = client.post("/jobs/process-pending", headers=headers).json()
    assert result["succeeded"] == 1
    fetched = client.get(f"/jobs/{job['id']}", headers=headers).json()
    assert fetched["status"] == "succeeded"


def test_pii_redact_tickets_job(client, db_session):
    headers = _admin_headers(client)
    ticket = _make_ticket(
        db_session, body="contact me at user@example.com", title="Help"
    )
    db_session.add(
        TicketChunk(ticket_id=ticket.id, chunk_index=0, text="contact me at user@example.com")
    )
    db_session.commit()

    client.post("/jobs", json={"job_type": "pii_redact_tickets"}, headers=headers)
    result = client.post("/jobs/process-pending", headers=headers).json()
    assert result["succeeded"] == 1
    payload = result["jobs"][0]
    assert '"tickets_redacted": 1' in payload["result_json"]

    db_session.expire_all()
    refreshed = db_session.get(Ticket, ticket.id)
    assert "user@example.com" not in refreshed.body
    assert "[REDACTED_EMAIL]" in refreshed.body


def test_connector_sync_job_missing_connector_fails(client, db_session):
    headers = _admin_headers(client)
    client.post(
        "/jobs",
        json={"job_type": "connector_sync", "payload": {"connector_id": "x"}},
        headers=headers,
    )
    result = client.post("/jobs/process-pending", headers=headers).json()
    assert result["failed"] == 1
    assert result["jobs"][0]["status"] == "failed"
    assert result["jobs"][0]["error"]


def test_list_jobs_filter_by_status(client, db_session):
    headers = _admin_headers(client)
    client.post("/jobs", json={"job_type": "retention_run"}, headers=headers)
    client.post("/jobs/process-pending", headers=headers)
    succeeded = client.get("/jobs?status=succeeded", headers=headers).json()
    assert len(succeeded["jobs"]) == 1
    assert succeeded["jobs"][0]["status"] == "succeeded"
