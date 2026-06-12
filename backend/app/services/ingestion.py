"""Shared ticket ingestion: chunk, embed, and de-duplicate.

Used by connector syncs (and reusable by CSV upload). Keeps the embed/chunk
logic in one place so every ingestion path behaves consistently.
"""
import json
from dataclasses import dataclass, field

from sqlalchemy.orm import Session

from app.models.models import Ticket, TicketChunk
from app.services.chunking import build_ticket_text, chunk_text, estimate_tokens
from app.services.dedup import DEFAULT_DEDUP_THRESHOLD, find_semantic_duplicate
from app.services.providers.base import EmbeddingProvider
from app.services.providers.factory import get_embedding_provider


@dataclass
class IngestResult:
    imported: int = 0
    duplicate_id: int = 0
    duplicate_semantic: int = 0
    embedding_failures: int = 0
    imported_ids: list[str] = field(default_factory=list)
    skipped_ids: list[str] = field(default_factory=list)


def _store_chunks(
    db: Session, ticket: Ticket, text_chunks: list[str], embeddings: list[list[float] | None]
) -> None:
    for idx, (chunk_str, emb) in enumerate(zip(text_chunks, embeddings)):
        db.add(
            TicketChunk(
                ticket_id=ticket.id,
                chunk_index=idx,
                text=chunk_str,
                embedding=json.dumps(emb) if emb else None,
                token_count=estimate_tokens(chunk_str),
            )
        )


def ingest_normalized_tickets(
    db: Session,
    rows: list[dict],
    *,
    ingestion_batch_id=None,
    semantic_dedup: bool = True,
    semantic_threshold: float = DEFAULT_DEDUP_THRESHOLD,
    provider: EmbeddingProvider | None = None,
    workspace_id=None,
) -> IngestResult:
    """Ingest already-validated, normalized ticket dicts.

    Each row must contain: id, title, body, product_area, issue_type, priority,
    customer_tier, status, resolution, created_at (datetime), resolved_at.
    """
    provider = provider or get_embedding_provider()
    result = IngestResult()

    existing_ids: set[str] = {tid for (tid,) in db.query(Ticket.id).all()}

    for row in rows:
        tid = str(row["id"]).strip()
        if not tid or tid in existing_ids:
            result.duplicate_id += 1
            result.skipped_ids.append(tid)
            continue

        ticket = Ticket(
            id=tid,
            workspace_id=workspace_id,
            title=row["title"],
            body=row["body"],
            product_area=row["product_area"],
            issue_type=row["issue_type"],
            priority=row["priority"],
            customer_tier=row["customer_tier"],
            status=row["status"],
            resolution=row.get("resolution", "") or "",
            created_at=row["created_at"],
            resolved_at=row.get("resolved_at"),
            ingestion_batch_id=ingestion_batch_id,
            validation_status="valid",
        )

        text_chunks = chunk_text(build_ticket_text(ticket))
        try:
            embeddings: list[list[float] | None] = list(provider.embed_texts(text_chunks))
        except Exception:
            result.embedding_failures += 1
            embeddings = [None] * len(text_chunks)

        if semantic_dedup:
            first_emb = next((e for e in embeddings if e is not None), None)
            if first_emb is not None:
                dup = find_semantic_duplicate(db, first_emb, semantic_threshold)
                if dup is not None:
                    result.duplicate_semantic += 1
                    result.skipped_ids.append(tid)
                    continue

        db.add(ticket)
        db.flush()
        _store_chunks(db, ticket, text_chunks, embeddings)
        existing_ids.add(tid)
        result.imported += 1
        result.imported_ids.append(tid)

    return result
