"""Connector sync orchestration: fetch -> normalize -> ingest -> advance cursor."""
from datetime import datetime

from sqlalchemy.orm import Session

from app.models.models import Connector, IngestionBatch
from app.services.connectors.factory import get_source_connector
from app.services.ingestion import ingest_normalized_tickets


def run_connector_sync(db: Session, connector: Connector, limit: int = 6) -> dict:
    source = get_source_connector(connector.provider)
    raw_tickets, new_cursor = source.fetch_since(connector.cursor, limit=limit)
    rows = [source.normalize(rt) for rt in raw_tickets]

    batch = IngestionBatch(filename=f"{connector.provider} sync ({connector.name})")
    db.add(batch)
    db.flush()

    result = ingest_normalized_tickets(db, rows, ingestion_batch_id=batch.id)

    batch.total_count = len(rows)
    batch.valid_count = result.imported
    batch.duplicate_count = result.duplicate_id + result.duplicate_semantic
    batch.embedding_failure_count = result.embedding_failures
    batch.completed_at = datetime.now(tz=None)

    connector.cursor = new_cursor
    connector.last_synced_at = datetime.now(tz=None)
    connector.total_imported = (connector.total_imported or 0) + result.imported

    db.commit()

    return {
        "connector_id": connector.id,
        "batch_id": batch.id,
        "fetched": len(rows),
        "imported": result.imported,
        "duplicate_id": result.duplicate_id,
        "duplicate_semantic": result.duplicate_semantic,
        "embedding_failures": result.embedding_failures,
        "cursor": new_cursor,
        "imported_ids": result.imported_ids,
    }
