"""Add V4 workflow tables: connectors, ingestion_jobs, kb_articles

Revision ID: 004
Revises: 003
Create Date: 2026-05-28

"""
from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID

from alembic import op

revision: str = "004"
down_revision: str | None = "003"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "connectors",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("provider", sa.String(50), nullable=False),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("config_json", sa.Text, nullable=True),
        sa.Column("cursor", sa.String(100), nullable=True),
        sa.Column("enabled", sa.Boolean, nullable=False, server_default=sa.true()),
        sa.Column("last_synced_at", sa.DateTime, nullable=True),
        sa.Column("total_imported", sa.Integer, nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime, server_default=sa.func.now()),
    )
    op.create_table(
        "ingestion_jobs",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "connector_id",
            UUID(as_uuid=True),
            sa.ForeignKey("connectors.id"),
            nullable=False,
        ),
        sa.Column("interval_minutes", sa.Integer, nullable=False, server_default="60"),
        sa.Column("enabled", sa.Boolean, nullable=False, server_default=sa.true()),
        sa.Column("next_run_at", sa.DateTime, server_default=sa.func.now()),
        sa.Column("last_run_at", sa.DateTime, nullable=True),
        sa.Column("last_status", sa.String(50), nullable=True),
        sa.Column("last_imported", sa.Integer, nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime, server_default=sa.func.now()),
    )
    op.create_table(
        "kb_articles",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("title", sa.String(500), nullable=False),
        sa.Column("product_area", sa.String(200), nullable=False),
        sa.Column("issue_type", sa.String(200), nullable=False, server_default=""),
        sa.Column("summary", sa.Text, nullable=False),
        sa.Column("resolution_steps", sa.Text, nullable=False, server_default=""),
        sa.Column("source_ticket_ids_json", sa.Text, nullable=True),
        sa.Column("ticket_count", sa.Integer, nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime, server_default=sa.func.now()),
    )


def downgrade() -> None:
    op.drop_table("kb_articles")
    op.drop_table("ingestion_jobs")
    op.drop_table("connectors")
