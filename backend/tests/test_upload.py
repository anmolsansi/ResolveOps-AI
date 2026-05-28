import io


def _make_csv(rows: list[dict], include_header: bool = True) -> io.BytesIO:
    cols = [
        "id", "title", "body", "product_area", "issue_type",
        "priority", "customer_tier", "status", "resolution",
        "created_at", "resolved_at",
    ]
    lines = []
    if include_header:
        lines.append(",".join(cols))
    for row in rows:
        values = [str(row.get(c, "")) for c in cols]
        lines.append(",".join(values))
    content = "\n".join(lines).encode("utf-8")
    return io.BytesIO(content)


VALID_ROW = {
    "id": "T-1",
    "title": "Login fails",
    "body": "Cannot log in with valid credentials",
    "product_area": "Auth",
    "issue_type": "Bug",
    "priority": "High",
    "customer_tier": "Enterprise",
    "status": "Open",
    "resolution": "Reset password",
    "created_at": "2025-01-15",
    "resolved_at": "2025-01-16",
}


def test_upload_valid_csv(client):
    csv_file = _make_csv([VALID_ROW])
    resp = client.post(
        "/tickets/upload",
        files={"file": ("tickets.csv", csv_file, "text/csv")},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["valid_count"] == 1
    assert data["invalid_count"] == 0
    assert data["duplicate_count"] == 0


def test_upload_missing_field(client):
    row = {**VALID_ROW, "title": ""}
    csv_file = _make_csv([row])
    resp = client.post(
        "/tickets/upload",
        files={"file": ("tickets.csv", csv_file, "text/csv")},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["invalid_count"] == 1
    assert len(data["errors"]) == 1


def test_upload_invalid_date(client):
    row = {**VALID_ROW, "id": "T-BAD", "created_at": "not-a-date"}
    csv_file = _make_csv([row])
    resp = client.post(
        "/tickets/upload",
        files={"file": ("tickets.csv", csv_file, "text/csv")},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["invalid_count"] == 1


def test_upload_duplicate(client):
    csv_file = _make_csv([VALID_ROW, VALID_ROW])
    resp = client.post(
        "/tickets/upload",
        files={"file": ("tickets.csv", csv_file, "text/csv")},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["valid_count"] == 1
    assert data["duplicate_count"] == 1
