from app.services.chunking import build_ticket_text, chunk_text, estimate_tokens


class _FakeTicket:
    def __init__(self, **kwargs):
        self.title = kwargs.get("title", "Test Title")
        self.product_area = kwargs.get("product_area", "Billing")
        self.issue_type = kwargs.get("issue_type", "Bug")
        self.priority = kwargs.get("priority", "High")
        self.customer_tier = kwargs.get("customer_tier", "Enterprise")
        self.status = kwargs.get("status", "Open")
        self.resolution = kwargs.get("resolution", "")
        self.body = kwargs.get("body", "Test body text")


def test_build_ticket_text_includes_all_fields():
    t = _FakeTicket(resolution="Fixed the issue")
    text = build_ticket_text(t)
    assert "Title: Test Title" in text
    assert "Product Area: Billing" in text
    assert "Issue Type: Bug" in text
    assert "Priority: High" in text
    assert "Customer Tier: Enterprise" in text
    assert "Status: Open" in text
    assert "Resolution: Fixed the issue" in text
    assert "Body: Test body text" in text


def test_build_ticket_text_no_resolution():
    t = _FakeTicket(resolution="")
    text = build_ticket_text(t)
    assert "Resolution:" not in text


def test_chunk_text_short():
    text = "This is a short text"
    chunks = chunk_text(text)
    assert len(chunks) == 1
    assert chunks[0] == text


def test_chunk_text_long():
    words = ["word"] * 2000
    text = " ".join(words)
    chunks = chunk_text(text)
    assert len(chunks) > 1
    for chunk in chunks:
        assert len(chunk.split()) <= 800


def test_chunk_text_overlap():
    words = [f"w{i}" for i in range(1600)]
    text = " ".join(words)
    chunks = chunk_text(text)
    assert len(chunks) >= 2
    first_words = set(chunks[0].split()[-100:])
    second_words = set(chunks[1].split()[:100])
    assert len(first_words & second_words) > 0


def test_estimate_tokens():
    text = "one two three four"
    tokens = estimate_tokens(text)
    assert tokens >= 1
    assert isinstance(tokens, int)


def test_estimate_tokens_empty():
    assert estimate_tokens("") == 1
