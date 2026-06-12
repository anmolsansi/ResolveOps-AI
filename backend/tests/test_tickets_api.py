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
        "title": f"Issue {i}",
        "body": f"Description for issue {i}",
        "product_area": "Billing" if i % 2 == 0 else "Auth",
        "issue_type": "Bug",
        "priority": "High",
        "customer_tier": "Enterprise",
        "status": "Open",
        "resolution": "Fixed",
        "created_at": f"2025-01-{15 + i:02d}",
        "resolved_at": f"2025-01-{16 + i:02d}",
    }
    for i in range(5)
]


def test_list_tickets(client, auth_headers):
    _upload(client, ROWS, auth_headers)
    resp = client.get("/tickets", headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["total"] == 5
    assert len(data["items"]) == 5


def test_list_tickets_filter(client, auth_headers):
    _upload(client, ROWS, auth_headers)
    resp = client.get("/tickets?product_area=Billing", headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert all(t["product_area"] == "Billing" for t in data["items"])


def test_list_tickets_search(client, auth_headers):
    _upload(client, ROWS, auth_headers)
    resp = client.get("/tickets?search=Issue 3", headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["total"] >= 1


def test_list_tickets_pagination(client, auth_headers):
    _upload(client, ROWS, auth_headers)
    resp = client.get("/tickets?page=1&page_size=2", headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert len(data["items"]) == 2
    assert data["page"] == 1
    assert data["page_size"] == 2


def test_get_ticket_detail(client, auth_headers):
    _upload(client, ROWS[:1], auth_headers)
    resp = client.get("/tickets/T-0", headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["id"] == "T-0"
    assert "chunks" in data


def test_get_ticket_not_found(client, auth_headers):
    resp = client.get("/tickets/NONEXISTENT", headers=auth_headers)
    assert resp.status_code == 404


def test_tickets_requires_auth(client):
    resp = client.get("/tickets")
    assert resp.status_code == 401
