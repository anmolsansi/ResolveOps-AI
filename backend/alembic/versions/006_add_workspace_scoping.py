"""Add workspace_id to all data models for multi-tenant workspace scoping.

Adds a nullable workspace_id FK column to: ingestion_batches, tickets,
rag_queries, connectors, kb_articles, eval_runs, saved_eval_questions,
background_jobs, and prompt_templates.

Revision ID: 006
Revises: 005
Create Date: 2026-06-12

"""
from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID

from alembic import op

revision: str = "006"
down_revision: str | None = "005"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # Add workspace_id FK to tables that don't have it yet
    for table in [
        "ingestion_batches",
        "tickets",
        "rag_queries",
        "connectors",
        "kb_articles",
        "eval_runs",
        "saved_eval_questions",
        "background_jobs",
        "prompt_templates",
    ]:
        op.add_column(
            table,
            sa.Column("workspace_id", UUID(as_uuid=True), nullable=True),
        )
        op.create_index(
            f"ix_{table}_workspace_id",
            table,
            ["workspace_id"],
        )
        op.create_foreign_key(
            f"fk_{table}_workspace_id",
            table,
            "workspaces",
            ["workspace_id"],
            ["id"],
            ondelete="SET NULL",
        )


def downgrade() -> None:
    for table in [
        "prompt_templates",
        "background_jobs",
        "saved_eval_questions",
        "eval_runs",
        "kb_articles",
        "connectors",
        "rag_queries",
        "tickets",
        "ingestion_batches",
    ]:
        op.drop_constraint(f"fk_{table}_workspace_id", table, type_="foreignkey")
        op.drop_index(f"ix_{table}_workspace_id", table_name=table)
        op.drop_column(table, "workspace_id")
