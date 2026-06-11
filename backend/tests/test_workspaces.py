def _token(client, email, role=None):
    body = {"email": email, "password": "password123"}
    if role:
        body["role"] = role
    return client.post("/auth/register", json=body).json()["access_token"]


def _headers(token):
    return {"Authorization": f"Bearer {token}"}


def test_create_workspace_makes_creator_admin(client):
    token = _token(client, "owner@example.com")
    resp = client.post("/workspaces", json={"name": "Acme Support"}, headers=_headers(token))
    assert resp.status_code == 200
    data = resp.json()
    assert data["slug"] == "acme-support"
    assert data["member_count"] == 1


def test_duplicate_slug_rejected(client):
    token = _token(client, "owner@example.com")
    client.post("/workspaces", json={"name": "Acme"}, headers=_headers(token))
    dup = client.post("/workspaces", json={"name": "Acme"}, headers=_headers(token))
    assert dup.status_code == 409


def test_add_and_list_members(client):
    admin_token = _token(client, "owner@example.com")
    _token(client, "agent@example.com")  # create the user to be added
    ws = client.post("/workspaces", json={"name": "Acme"}, headers=_headers(admin_token)).json()
    ws_id = ws["id"]

    add = client.post(
        f"/workspaces/{ws_id}/members",
        json={"email": "agent@example.com", "role": "member"},
        headers=_headers(admin_token),
    )
    assert add.status_code == 200

    members = client.get(f"/workspaces/{ws_id}/members", headers=_headers(admin_token)).json()
    emails = {m["email"] for m in members["members"]}
    assert emails == {"owner@example.com", "agent@example.com"}


def test_add_unknown_user_404(client):
    admin_token = _token(client, "owner@example.com")
    ws = client.post("/workspaces", json={"name": "Acme"}, headers=_headers(admin_token)).json()
    resp = client.post(
        f"/workspaces/{ws['id']}/members",
        json={"email": "ghost@example.com"},
        headers=_headers(admin_token),
    )
    assert resp.status_code == 404


def test_member_cannot_add_members(client):
    admin_token = _token(client, "owner@example.com")
    member_token = _token(client, "agent@example.com")
    ws = client.post("/workspaces", json={"name": "Acme"}, headers=_headers(admin_token)).json()
    client.post(
        f"/workspaces/{ws['id']}/members",
        json={"email": "agent@example.com", "role": "member"},
        headers=_headers(admin_token),
    )
    # member tries to add someone
    _token(client, "third@example.com")
    resp = client.post(
        f"/workspaces/{ws['id']}/members",
        json={"email": "third@example.com"},
        headers=_headers(member_token),
    )
    assert resp.status_code == 403


def test_update_and_remove_member(client):
    admin_token = _token(client, "owner@example.com")
    _token(client, "agent@example.com")
    ws = client.post("/workspaces", json={"name": "Acme"}, headers=_headers(admin_token)).json()
    add = client.post(
        f"/workspaces/{ws['id']}/members",
        json={"email": "agent@example.com", "role": "member"},
        headers=_headers(admin_token),
    ).json()
    mid = add["membership_id"]

    upd = client.put(
        f"/workspaces/{ws['id']}/members/{mid}",
        json={"role": "admin"},
        headers=_headers(admin_token),
    )
    assert upd.status_code == 200
    assert upd.json()["role"] == "admin"

    rem = client.delete(f"/workspaces/{ws['id']}/members/{mid}", headers=_headers(admin_token))
    assert rem.status_code == 200


def test_non_admin_global_user_sees_only_their_workspaces(client):
    admin_token = _token(client, "owner@example.com")
    member_token = _token(client, "agent@example.com")
    client.post("/workspaces", json={"name": "Private"}, headers=_headers(admin_token))
    # member has no workspaces yet
    listing = client.get("/workspaces", headers=_headers(member_token)).json()
    assert listing["workspaces"] == []
