"""Vector-search backend selection: pgvector on Postgres, in-memory fallback.

Production deployments on PostgreSQL with the ``vector`` extension get
approximate-nearest-neighbour retrieval via an indexed ``embedding_vec`` column.
Everywhere else (SQLite, mock mode, missing extension) we transparently fall
back to in-Python cosine similarity over JSON-encoded embeddings.
"""
from __future__ import annotations

from sqlalchemy import text
from sqlalchemy.orm import Session

from app.services.settings_store import get_setting


def pgvector_importable() -> bool:
    try:
        import pgvector  # noqa: F401

        return True
    except ImportError:
        return False


def _extension_present(db: Session) -> bool:
    if db.bind is None or db.bind.dialect.name != "postgresql":
        return False
    try:
        row = db.execute(
            text("SELECT 1 FROM pg_extension WHERE extname = 'vector'")
        ).first()
        return row is not None
    except Exception:  # noqa: BLE001 - any failure means treat as unavailable
        return False


def active_backend(db: Session) -> str:
    """Return the backend actually in use: 'pgvector' or 'memory'."""
    configured = str(get_setting(db, "vector_backend"))
    dialect = db.bind.dialect.name if db.bind is not None else "unknown"
    if configured == "memory":
        return "memory"
    if dialect != "postgresql":
        return "memory"
    if not (_extension_present(db) and pgvector_importable()):
        return "memory"
    # configured == "pgvector" or "auto" with everything available
    return "pgvector"


def backend_status(db: Session) -> dict:
    configured = str(get_setting(db, "vector_backend"))
    dialect = db.bind.dialect.name if db.bind is not None else "unknown"
    active = active_backend(db)
    reason = "in use" if active == "pgvector" else _fallback_reason(db, configured, dialect)
    return {
        "configured": configured,
        "dialect": dialect,
        "pgvector_importable": pgvector_importable(),
        "extension_present": _extension_present(db),
        "active_backend": active,
        "reason": reason,
    }


def _fallback_reason(db: Session, configured: str, dialect: str) -> str:
    if configured == "memory":
        return "explicitly configured to memory"
    if dialect != "postgresql":
        return f"dialect '{dialect}' is not postgresql"
    if not pgvector_importable():
        return "pgvector python package not installed"
    if not _extension_present(db):
        return "vector extension not enabled in database"
    return "fallback"


def pgvector_candidate_ids(
    db: Session, q_embedding: list[float], top_k: int
) -> list[str]:
    """Return chunk ids ordered by vector distance (Postgres + pgvector only)."""
    literal = "[" + ",".join(str(x) for x in q_embedding) + "]"
    rows = db.execute(
        text(
            "SELECT id FROM ticket_chunks "
            "WHERE embedding_vec IS NOT NULL "
            "ORDER BY embedding_vec <=> :q "
            "LIMIT :k"
        ),
        {"q": literal, "k": top_k},
    ).fetchall()
    return [str(r[0]) for r in rows]
