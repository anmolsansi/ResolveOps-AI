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


def test_list_tickets(client):
    _upload(client, ROWS)
    resp = client.get("/tickets")
    assert resp.status_code == 200
    data = resp.json()
    assert data["total"] == 5
    assert len(data["items"]) == 5


def test_list_tickets_filter(client):
    _upload(client, ROWS)
    resp = client.get("/tickets?product_area=Billing")
    assert resp.status_code == 200
    data = resp.json()
    assert all(t["product_area"] == "Billing" for t in data["items"])


def test_list_tickets_search(client):
    _upload(client, ROWS)
    resp = client.get("/tickets?search=Issue 3")
    assert resp.status_code == 200
    data = resp.json()
    assert data["total"] >= 1


def test_list_tickets_pagination(client):
    _upload(client, ROWS)
    resp = client.get("/tickets?page=1&page_size=2")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data["items"]) == 2
    assert data["page"] == 1
    assert data["page_size"] == 2


def test_get_ticket_detail(client):
    _upload(client, ROWS[:1])
    resp = client.get("/tickets/T-0")
    assert resp.status_code == 200
    data = resp.json()
    assert data["id"] == "T-0"
    assert "chunks" in data


def test_get_ticket_not_found(client):
    resp = client.get("/tickets/NONEXISTENT")
    assert resp.status_code == 404
