import json
import math

from sqlalchemy import and_
from sqlalchemy.orm import Session

from app.models.models import Ticket, TicketChunk
from app.services.providers.factory import get_embedding_provider


def cosine_similarity(a: list[float], b: list[float]) -> float:
    dot = sum(x * y for x, y in zip(a, b))
    norm_a = math.sqrt(sum(x * x for x in a))
    norm_b = math.sqrt(sum(x * x for x in b))
    if norm_a < 1e-10 or norm_b < 1e-10:
        return 0.0
    return dot / (norm_a * norm_b)


def _parse_embedding(raw: str | None) -> list[float] | None:
    if not raw:
        return None
    try:
        return json.loads(raw)
    except (json.JSONDecodeError, TypeError):
        return None


def retrieve_chunks(
    db: Session,
    question: str,
    filters: dict[str, str | None] | None = None,
    top_k: int = 5,
) -> list[dict]:
    provider = get_embedding_provider()
    q_embedding = provider.embed_texts([question])[0]

    filter_conditions = []
    if filters:
        filter_map = {
            "product_area": Ticket.product_area,
            "issue_type": Ticket.issue_type,
            "priority": Ticket.priority,
            "customer_tier": Ticket.customer_tier,
            "status": Ticket.status,
        }
        for key, col in filter_map.items():
            val = filters.get(key)
            if val:
                filter_conditions.append(col == val)

    query = db.query(TicketChunk).join(Ticket, TicketChunk.ticket_id == Ticket.id)
    if filter_conditions:
        query = query.filter(and_(*filter_conditions))
    chunks = query.all()

    scored: list[tuple[float, TicketChunk]] = []
    for chunk in chunks:
        c_emb = _parse_embedding(chunk.embedding)
        if c_emb is None:
            continue
        score = cosine_similarity(q_embedding, c_emb)
        scored.append((score, chunk))

    scored.sort(key=lambda x: x[0], reverse=True)
    top = scored[:top_k]

    results = []
    for score, chunk in top:
        results.append(
            {
                "chunk_id": chunk.id,
                "ticket_id": chunk.ticket_id,
                "score": round(score, 4),
                "preview": chunk.text[:300],
                "text": chunk.text,
            }
        )
    return results


def compute_confidence(scores: list[float]) -> float:
    if not scores:
        return 0.0
    avg = sum(scores) / len(scores)
    return round(min(max(avg, 0.0), 1.0), 4)
