"""Initial schema

Revision ID: 001
Revises:
Create Date: 2026-05-28

"""
from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID

from alembic import op

revision: str = "001"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "ingestion_batches",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("filename", sa.String(500), nullable=False),
        sa.Column("total_count", sa.Integer, default=0),
        sa.Column("valid_count", sa.Integer, default=0),
        sa.Column("invalid_count", sa.Integer, default=0),
        sa.Column("duplicate_count", sa.Integer, default=0),
        sa.Column("embedding_failure_count", sa.Integer, default=0),
        sa.Column("started_at", sa.DateTime, server_default=sa.func.now()),
        sa.Column("completed_at", sa.DateTime, nullable=True),
    )

    op.create_table(
        "tickets",
        sa.Column("id", sa.String(200), primary_key=True),
        sa.Column("title", sa.String(1000), nullable=False),
        sa.Column("body", sa.Text, nullable=False),
        sa.Column("product_area", sa.String(200), nullable=False),
        sa.Column("issue_type", sa.String(200), nullable=False),
        sa.Column("priority", sa.String(50), nullable=False),
        sa.Column("customer_tier", sa.String(100), nullable=False),
        sa.Column("status", sa.String(100), nullable=False),
        sa.Column("resolution", sa.Text, nullable=True),
        sa.Column("created_at", sa.DateTime, nullable=False),
        sa.Column("resolved_at", sa.DateTime, nullable=True),
        sa.Column("source_row_number", sa.Integer, nullable=True),
        sa.Column(
            "ingestion_batch_id",
            UUID(as_uuid=True),
            sa.ForeignKey("ingestion_batches.id"),
            nullable=True,
        ),
        sa.Column("validation_status", sa.String(50), default="valid"),
        sa.Column("validation_errors", sa.Text, nullable=True),
        sa.Column("inserted_at", sa.DateTime, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime, server_default=sa.func.now()),
    )
    op.create_index("ix_tickets_product_area", "tickets", ["product_area"])
    op.create_index("ix_tickets_issue_type", "tickets", ["issue_type"])
    op.create_index("ix_tickets_priority", "tickets", ["priority"])
    op.create_index("ix_tickets_customer_tier", "tickets", ["customer_tier"])
    op.create_index("ix_tickets_status", "tickets", ["status"])

    op.create_table(
        "ticket_chunks",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "ticket_id", sa.String(200), sa.ForeignKey("tickets.id"), nullable=False
        ),
        sa.Column("chunk_index", sa.Integer, nullable=False),
        sa.Column("text", sa.Text, nullable=False),
        sa.Column("embedding", sa.Text, nullable=True),
        sa.Column("token_count", sa.Integer, default=0),
        sa.Column("created_at", sa.DateTime, server_default=sa.func.now()),
    )

    op.create_table(
        "rag_queries",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("question", sa.Text, nullable=False),
        sa.Column("filters_json", sa.Text, nullable=True),
        sa.Column("answer", sa.Text, nullable=False),
        sa.Column("cited_ticket_ids_json", sa.Text, nullable=True),
        sa.Column("retrieved_chunk_ids_json", sa.Text, nullable=True),
        sa.Column("confidence", sa.Float, default=0.0),
        sa.Column("latency_ms", sa.Integer, default=0),
        sa.Column("estimated_cost_usd", sa.Float, default=0.0),
        sa.Column("created_at", sa.DateTime, server_default=sa.func.now()),
    )

    op.create_table(
        "eval_runs",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("name", sa.String(500), default=""),
        sa.Column("total_questions", sa.Integer, default=0),
        sa.Column("passed_count", sa.Integer, default=0),
        sa.Column("failed_count", sa.Integer, default=0),
        sa.Column("average_confidence", sa.Float, default=0.0),
        sa.Column("average_latency_ms", sa.Float, default=0.0),
        sa.Column("results_json", sa.Text, nullable=True),
        sa.Column("created_at", sa.DateTime, server_default=sa.func.now()),
    )


def downgrade() -> None:
    op.drop_table("eval_runs")
    op.drop_table("rag_queries")
    op.drop_table("ticket_chunks")
    op.drop_index("ix_tickets_status", "tickets")
    op.drop_index("ix_tickets_customer_tier", "tickets")
    op.drop_index("ix_tickets_priority", "tickets")
    op.drop_index("ix_tickets_issue_type", "tickets")
    op.drop_index("ix_tickets_product_area", "tickets")
    op.drop_table("tickets")
    op.drop_table("ingestion_batches")
