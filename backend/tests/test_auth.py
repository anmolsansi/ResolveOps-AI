def _register(client, email, password="password123", role=None):
    body = {"email": email, "password": password}
    if role:
        body["role"] = role
    return client.post("/auth/register", json=body)


def test_first_user_becomes_admin(client):
    resp = _register(client, "owner@example.com")
    assert resp.status_code == 200
    data = resp.json()
    assert data["role"] == "admin"
    assert data["access_token"]
    assert data["token_type"] == "bearer"


def test_second_user_defaults_to_member(client):
    _register(client, "owner@example.com")
    resp = _register(client, "member@example.com")
    assert resp.status_code == 200
    assert resp.json()["role"] == "member"


def test_duplicate_email_rejected(client):
    _register(client, "owner@example.com")
    resp = _register(client, "owner@example.com")
    assert resp.status_code == 409


def test_short_password_rejected(client):
    resp = _register(client, "owner@example.com", password="short")
    assert resp.status_code == 422


def test_login_success_and_wrong_password(client):
    _register(client, "owner@example.com")
    ok = client.post("/auth/login", json={"email": "owner@example.com", "password": "password123"})
    assert ok.status_code == 200
    assert ok.json()["role"] == "admin"

    bad = client.post("/auth/login", json={"email": "owner@example.com", "password": "nope"})
    assert bad.status_code == 401


def test_me_requires_token(client):
    assert client.get("/auth/me").status_code == 401

    token = _register(client, "owner@example.com").json()["access_token"]
    me = client.get("/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert me.status_code == 200
    assert me.json()["email"] == "owner@example.com"


def test_invalid_token_rejected(client):
    _register(client, "owner@example.com")
    resp = client.get("/auth/me", headers={"Authorization": "Bearer not.a.token"})
    assert resp.status_code == 401


def test_admin_can_list_and_change_roles(client):
    admin_token = _register(client, "owner@example.com").json()["access_token"]
    _register(client, "member@example.com")
    headers = {"Authorization": f"Bearer {admin_token}"}

    users = client.get("/auth/users", headers=headers)
    assert users.status_code == 200
    members = [u for u in users.json()["users"] if u["email"] == "member@example.com"]
    assert members and members[0]["role"] == "member"
    member_id = members[0]["id"]

    upd = client.put(
        f"/auth/users/{member_id}/role", json={"role": "admin"}, headers=headers
    )
    assert upd.status_code == 200
    assert upd.json()["role"] == "admin"


def test_member_cannot_list_users(client):
    _register(client, "owner@example.com")
    member_token = _register(client, "member@example.com").json()["access_token"]
    resp = client.get("/auth/users", headers={"Authorization": f"Bearer {member_token}"})
    assert resp.status_code == 403
