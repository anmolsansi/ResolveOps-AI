"""Semantic ticket de-duplication.

Uses the same cosine similarity over chunk embeddings that powers retrieval.
In mock mode embeddings are deterministic, so tickets with identical content
produce identical embeddings (cosine 1.0) and are flagged as duplicates, while
unrelated tickets stay near-orthogonal.
"""
from sqlalchemy.orm import Session

from app.models.models import Ticket, TicketChunk
from app.services.retrieval import _parse_embedding, cosine_similarity

DEFAULT_DEDUP_THRESHOLD = 0.92


def _representative_embeddings(db: Session, workspace_id=None) -> dict[str, list[float]]:
    """First embedded chunk per ticket, used as the ticket's representative vector."""
    query = (
        db.query(TicketChunk)
        .filter(TicketChunk.embedding.isnot(None))
    )
    if workspace_id is not None:
        query = query.join(Ticket, TicketChunk.ticket_id == Ticket.id).filter(
            Ticket.workspace_id == workspace_id
        )
    rows = (
        query
        .order_by(TicketChunk.ticket_id, TicketChunk.chunk_index)
        .all()
    )
    reps: dict[str, list[float]] = {}
    for chunk in rows:
        if chunk.ticket_id in reps:
            continue
        emb = _parse_embedding(chunk.embedding)
        if emb is not None:
            reps[chunk.ticket_id] = emb
    return reps


def find_semantic_duplicate(
    db: Session,
    embedding: list[float],
    threshold: float = DEFAULT_DEDUP_THRESHOLD,
    exclude_ticket_id: str | None = None,
) -> tuple[str, float] | None:
    """Return (ticket_id, score) of the closest existing ticket above threshold."""
    best: tuple[str, float] | None = None
    for ticket_id, emb in _representative_embeddings(db).items():
        if ticket_id == exclude_ticket_id:
            continue
        score = cosine_similarity(embedding, emb)
        if score >= threshold and (best is None or score > best[1]):
            best = (ticket_id, score)
    return best


def find_duplicate_clusters(
    db: Session, threshold: float = DEFAULT_DEDUP_THRESHOLD, workspace_id=None
) -> list[dict]:
    """Group tickets whose representative embeddings are mutually similar."""
    reps = _representative_embeddings(db, workspace_id=workspace_id)
    ticket_ids = sorted(reps.keys())
    parent: dict[str, str] = {tid: tid for tid in ticket_ids}

    def find(x: str) -> str:
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    def union(a: str, b: str) -> None:
        ra, rb = find(a), find(b)
        if ra != rb:
            parent[max(ra, rb)] = min(ra, rb)

    pair_scores: dict[tuple[str, str], float] = {}
    for i, a in enumerate(ticket_ids):
        for b in ticket_ids[i + 1 :]:
            score = cosine_similarity(reps[a], reps[b])
            if score >= threshold:
                pair_scores[(a, b)] = round(score, 4)
                union(a, b)

    groups: dict[str, list[str]] = {}
    for tid in ticket_ids:
        groups.setdefault(find(tid), []).append(tid)

    tickets = {
        t.id: t
        for t in db.query(Ticket).filter(Ticket.id.in_(ticket_ids)).all()
    }
    clusters: list[dict] = []
    for members in groups.values():
        if len(members) < 2:
            continue
        members = sorted(members)
        max_score = max(
            (pair_scores.get((a, b), 0.0) for a in members for b in members if a < b),
            default=0.0,
        )
        clusters.append(
            {
                "ticket_ids": members,
                "size": len(members),
                "max_similarity": max_score,
                "tickets": [
                    {
                        "id": tid,
                        "title": tickets[tid].title if tid in tickets else tid,
                        "product_area": tickets[tid].product_area if tid in tickets else "",
                    }
                    for tid in members
                ],
            }
        )
    clusters.sort(key=lambda c: (-c["size"], -c["max_similarity"]))
    return clusters
