import json
import math
import re

from sqlalchemy import and_
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.models import Ticket, TicketChunk
from app.services.providers.factory import get_embedding_provider

MAX_KEYWORD_BOOST = 0.7
STOPWORDS = frozenset(
    "a an the is are was were be been being have has had do does did will would "
    "shall should may might can could and or but not no nor so yet for of in on "
    "at to from by with about into through during before after above below between "
    "out off over under again further then once here there when where why how all "
    "each every both few more most other some such what which who whom this that "
    "these those i me my myself we our ours ourselves you your yours yourself "
    "yourselves he him his himself she her hers herself it its itself they them "
    "their theirs themselves am if up do fix resolve help get set make issue issues "
    "problem problems question questions".split()
)


def _tokenize(text: str) -> set[str]:
    return {w for w in re.findall(r"[a-z0-9]+", text.lower()) if w not in STOPWORDS}


def _keyword_boost(query_tokens: set[str], chunk_text: str) -> tuple[float, int, list[str]]:
    """Return (boost_score, hit_count, matched_tokens)."""
    if not query_tokens:
        return 0.0, 0, []
    chunk_tokens = _tokenize(chunk_text)
    matched = query_tokens & chunk_tokens
    hits = len(matched)
    overlap = hits / len(query_tokens)
    boost = min(overlap * MAX_KEYWORD_BOOST, 1.0)
    return boost, hits, sorted(matched)


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


def _is_mock_mode() -> bool:
    return settings.mock_providers or settings.embedding_provider == "mock"


def retrieve_chunks(
    db: Session,
    question: str,
    filters: dict[str, str | None] | None = None,
    top_k: int = 5,
) -> list[dict]:
    provider = get_embedding_provider()
    q_embedding = provider.embed_texts([question])[0]
    use_keyword_boost = _is_mock_mode()
    query_tokens = _tokenize(question) if use_keyword_boost else set()

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

    scored: list[tuple[float, TicketChunk, dict]] = []
    for chunk in chunks:
        c_emb = _parse_embedding(chunk.embedding)
        if c_emb is None:
            continue
        cos_score = cosine_similarity(q_embedding, c_emb)
        boost = 0.0
        keyword_hits = 0
        matched_tokens: list[str] = []
        if use_keyword_boost:
            boost, keyword_hits, matched_tokens = _keyword_boost(query_tokens, chunk.text)
        final_score = cos_score + boost
        debug = {
            "cosine_score": round(cos_score, 4),
            "keyword_boost": round(boost, 4),
            "keyword_hits": keyword_hits,
            "matched_tokens": matched_tokens,
        }
        scored.append((final_score, chunk, debug))

    scored.sort(key=lambda x: x[0], reverse=True)
    top = scored[:top_k]

    results = []
    for score, chunk, debug in top:
        results.append(
            {
                "chunk_id": chunk.id,
                "ticket_id": chunk.ticket_id,
                "score": round(score, 4),
                "preview": chunk.text[:300],
                "text": chunk.text,
                "debug": debug,
            }
        )
    return results


def compute_confidence(scores: list[float]) -> float:
    if not scores:
        return 0.0
    avg = sum(scores) / len(scores)
    return round(min(max(avg, 0.0), 1.0), 4)
