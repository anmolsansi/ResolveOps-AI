from app.models.models import Ticket

TARGET_CHUNK_WORDS = 800
OVERLAP_WORDS = 100


def build_ticket_text(ticket: Ticket) -> str:
    parts = [
        f"Title: {ticket.title}",
        f"Product Area: {ticket.product_area}",
        f"Issue Type: {ticket.issue_type}",
        f"Priority: {ticket.priority}",
        f"Customer Tier: {ticket.customer_tier}",
        f"Status: {ticket.status}",
    ]
    if ticket.resolution:
        parts.append(f"Resolution: {ticket.resolution}")
    parts.append(f"Body: {ticket.body}")
    return "\n".join(parts)


def chunk_text(text: str) -> list[str]:
    words = text.split()
    if len(words) <= TARGET_CHUNK_WORDS:
        return [text]
    chunks: list[str] = []
    start = 0
    while start < len(words):
        end = min(start + TARGET_CHUNK_WORDS, len(words))
        chunk = " ".join(words[start:end])
        chunks.append(chunk)
        if end >= len(words):
            break
        start = end - OVERLAP_WORDS
    return chunks


def estimate_tokens(text: str) -> int:
    return max(1, len(text.split()) * 4 // 3)
