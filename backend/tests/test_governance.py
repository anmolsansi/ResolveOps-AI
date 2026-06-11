from datetime import datetime, timedelta

from app.models.models import AuditLog, RagQuery


def _admin_headers(client):
    token = client.post(
        "/auth/register", json={"email": "owner@example.com", "password": "password123"}
    ).json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_settings_defaults_and_update(client):
    headers = _admin_headers(client)
    current = client.get("/settings", headers=headers)
    assert current.status_code == 200
    assert current.json()["vector_backend"] == "auto"

    upd = client.put(
        "/settings",
        json={"low_confidence_threshold": 0.42, "default_top_k": 7, "vector_backend": "memory"},
        headers=headers,
    )
    assert upd.status_code == 200
    data = upd.json()
    assert data["low_confidence_threshold"] == 0.42
    assert data["default_top_k"] == 7
    assert data["vector_backend"] == "memory"


def test_settings_update_requires_admin(client):
    client.post("/auth/register", json={"email": "owner@example.com", "password": "password123"})
    member_token = client.post(
        "/auth/register", json={"email": "m@example.com", "password": "password123"}
    ).json()["access_token"]
    resp = client.put(
        "/settings",
        json={"default_top_k": 3},
        headers={"Authorization": f"Bearer {member_token}"},
    )
    assert resp.status_code == 403


def test_vector_backend_status_is_memory_on_sqlite(client):
    headers = _admin_headers(client)
    resp = client.get("/settings/vector-backend", headers=headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["active_backend"] == "memory"
    assert data["dialect"] == "sqlite"


def test_audit_log_records_login(client):
    headers = _admin_headers(client)
    client.post("/auth/login", json={"email": "owner@example.com", "password": "password123"})
    logs = client.get("/audit", headers=headers).json()
    actions = {log["action"] for log in logs["logs"]}
    assert "user.register" in actions
    assert "user.login" in actions


def test_audit_requires_admin(client):
    client.post("/auth/register", json={"email": "owner@example.com", "password": "password123"})
    member_token = client.post(
        "/auth/register", json={"email": "m@example.com", "password": "password123"}
    ).json()["access_token"]
    resp = client.get("/audit", headers={"Authorization": f"Bearer {member_token}"})
    assert resp.status_code == 403


def test_retention_preview_and_run(client, db_session):
    headers = _admin_headers(client)
    # Configure a 30-day retention window for rag queries.
    client.put("/settings", json={"retention_rag_query_days": 30}, headers=headers)

    old = RagQuery(
        question="old", answer="a", confidence=0.5,
        created_at=datetime.utcnow() - timedelta(days=60),
    )
    recent = RagQuery(
        question="recent", answer="a", confidence=0.5,
        created_at=datetime.utcnow(),
    )
    db_session.add_all([old, recent])
    db_session.commit()

    preview = client.get("/retention", headers=headers).json()
    assert preview["rag_queries_to_purge"] == 1

    run = client.post("/retention/run", headers=headers).json()
    assert run["rag_queries_deleted"] == 1

    remaining = db_session.query(RagQuery).count()
    assert remaining == 1


def test_retention_disabled_when_days_zero(client, db_session):
    headers = _admin_headers(client)
    db_session.add(
        RagQuery(
            question="old", answer="a", confidence=0.5,
            created_at=datetime.utcnow() - timedelta(days=900),
        )
    )
    db_session.commit()
    preview = client.get("/retention", headers=headers).json()
    assert preview["rag_queries_to_purge"] == 0
    run = client.post("/retention/run", headers=headers).json()
    assert run["rag_queries_deleted"] == 0


def test_audit_purged_by_retention(client, db_session):
    headers = _admin_headers(client)
    client.put("/settings", json={"retention_audit_log_days": 10}, headers=headers)
    db_session.add(
        AuditLog(
            action="old.action",
            created_at=datetime.utcnow() - timedelta(days=40),
        )
    )
    db_session.commit()
    run = client.post("/retention/run", headers=headers).json()
    assert run["audit_logs_deleted"] >= 1
