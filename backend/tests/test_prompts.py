from app.services.prompts import DEFAULT_PROMPT, get_active_prompt_text


def _admin_headers(client):
    token = client.post(
        "/auth/register", json={"email": "owner@example.com", "password": "password123"}
    ).json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_default_prompt_when_none_active(client, db_session):
    assert get_active_prompt_text(db_session) == DEFAULT_PROMPT


def test_create_prompt_increments_version(client):
    headers = _admin_headers(client)
    v1 = client.post(
        "/prompts", json={"name": "support", "content": "first"}, headers=headers
    ).json()
    v2 = client.post(
        "/prompts", json={"name": "support", "content": "second"}, headers=headers
    ).json()
    assert v1["version"] == 1
    assert v2["version"] == 2


def test_activate_prompt_is_exclusive(client, db_session):
    headers = _admin_headers(client)
    p1 = client.post(
        "/prompts", json={"name": "support", "content": "first", "activate": True}, headers=headers
    ).json()
    p2 = client.post(
        "/prompts", json={"name": "support", "content": "second"}, headers=headers
    ).json()

    listing = client.get("/prompts", headers=headers).json()
    assert listing["active_id"] == p1["id"]
    assert get_active_prompt_text(db_session) == "first"

    client.post(f"/prompts/{p2['id']}/activate", headers=headers)
    listing2 = client.get("/prompts", headers=headers).json()
    assert listing2["active_id"] == p2["id"]
    # only one active at a time
    actives = [p for p in listing2["prompts"] if p["is_active"]]
    assert len(actives) == 1


def test_create_prompt_requires_admin(client):
    client.post("/auth/register", json={"email": "owner@example.com", "password": "password123"})
    member_token = client.post(
        "/auth/register", json={"email": "m@example.com", "password": "password123"}
    ).json()["access_token"]
    resp = client.post(
        "/prompts",
        json={"name": "x", "content": "y"},
        headers={"Authorization": f"Bearer {member_token}"},
    )
    assert resp.status_code == 403


def test_activate_unknown_prompt_404(client):
    headers = _admin_headers(client)
    resp = client.post(
        "/prompts/00000000-0000-0000-0000-000000000000/activate", headers=headers
    )
    assert resp.status_code == 404
