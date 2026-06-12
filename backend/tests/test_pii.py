from app.services.pii import detect_pii, redact_pii


def test_detect_email_phone_ssn():
    text = "Contact jane.doe@example.com or 415-555-0199, SSN 123-45-6789."
    types = {m["type"] for m in detect_pii(text)}
    assert "email" in types
    assert "phone" in types
    assert "ssn" in types


def test_detect_credit_card_and_ip():
    text = "Card 4111 1111 1111 1111 from host 192.168.0.1"
    types = {m["type"] for m in detect_pii(text)}
    assert "credit_card" in types
    assert "ip_address" in types


def test_redaction_replaces_with_placeholders():
    text = "Email me at a@b.com"
    redacted, counts = redact_pii(text)
    assert "a@b.com" not in redacted
    assert "[REDACTED_EMAIL]" in redacted
    assert counts.get("email") == 1


def test_clean_text_has_no_matches():
    redacted, counts = redact_pii("The login button does not work on mobile.")
    assert counts == {}
    assert redacted == "The login button does not work on mobile."


def test_scan_endpoint(client, auth_headers):
    resp = client.post("/pii/scan", json={"text": "reach me: x@y.com"}, headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["counts"].get("email") == 1
    assert "[REDACTED_EMAIL]" in data["redacted_text"]
    assert data["matches"][0]["type"] == "email"


def test_pii_requires_auth(client):
    resp = client.post("/pii/scan", json={"text": "test"})
    assert resp.status_code == 401
