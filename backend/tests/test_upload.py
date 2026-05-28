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


def test_upload_rejects_non_csv(client):
    resp = client.post(
        "/tickets/upload",
        files={"file": ("data.txt", io.BytesIO(b"hello"), "text/plain")},
    )
    assert resp.status_code == 400
    assert "CSV" in resp.json()["detail"]


def test_upload_missing_columns(client):
    content = b"id,title\nT-1,Test\n"
    resp = client.post(
        "/tickets/upload",
        files={"file": ("tickets.csv", io.BytesIO(content), "text/csv")},
    )
    assert resp.status_code == 400
    assert "Missing required columns" in resp.json()["detail"]


def test_upload_empty_csv(client):
    resp = client.post(
        "/tickets/upload",
        files={"file": ("tickets.csv", io.BytesIO(b""), "text/csv")},
    )
    assert resp.status_code == 400


def test_upload_multiple_invalid_fields(client):
    row = {**VALID_ROW, "id": "T-MULTI", "title": "", "body": "", "product_area": ""}
    csv_file = _make_csv([row])
    resp = client.post(
        "/tickets/upload",
        files={"file": ("tickets.csv", csv_file, "text/csv")},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["invalid_count"] == 1
    error_reason = data["errors"][0]["reason"]
    assert "title" in error_reason
    assert "body" in error_reason


def test_upload_creates_chunks(client):
    csv_file = _make_csv([VALID_ROW])
    resp = client.post(
        "/tickets/upload",
        files={"file": ("tickets.csv", csv_file, "text/csv")},
    )
    assert resp.status_code == 200
    detail = client.get("/tickets/T-1")
    assert detail.status_code == 200
    assert len(detail.json()["chunks"]) >= 1


def test_upload_batch_counts(client):
    rows = [
        VALID_ROW,
        {**VALID_ROW, "id": "T-2", "title": "Another valid"},
        {**VALID_ROW, "id": "T-3", "title": ""},  # invalid
    ]
    csv_file = _make_csv(rows)
    resp = client.post(
        "/tickets/upload",
        files={"file": ("tickets.csv", csv_file, "text/csv")},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["total_count"] == 3
    assert data["valid_count"] == 2
    assert data["invalid_count"] == 1


def test_upload_cross_batch_duplicate(client):
    csv1 = _make_csv([VALID_ROW])
    client.post("/tickets/upload", files={"file": ("batch1.csv", csv1, "text/csv")})

    csv2 = _make_csv([VALID_ROW])
    resp = client.post("/tickets/upload", files={"file": ("batch2.csv", csv2, "text/csv")})
    assert resp.status_code == 200
    data = resp.json()
    assert data["duplicate_count"] == 1
    assert data["valid_count"] == 0


def test_upload_empty_resolution_accepted(client):
    row = {**VALID_ROW, "id": "T-NORES", "resolution": ""}
    csv_file = _make_csv([row])
    resp = client.post(
        "/tickets/upload",
        files={"file": ("tickets.csv", csv_file, "text/csv")},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["valid_count"] == 1
    assert data["invalid_count"] == 0


def test_upload_various_date_formats(client):
    row1 = {**VALID_ROW, "id": "T-D1", "created_at": "2025-01-15 10:30:00"}
    row2 = {**VALID_ROW, "id": "T-D2", "created_at": "2025-01-15T10:30:00"}
    row3 = {**VALID_ROW, "id": "T-D3", "created_at": "01/15/2025"}
    csv_file = _make_csv([row1, row2, row3])
    resp = client.post(
        "/tickets/upload",
        files={"file": ("tickets.csv", csv_file, "text/csv")},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["valid_count"] == 3
    assert data["invalid_count"] == 0
