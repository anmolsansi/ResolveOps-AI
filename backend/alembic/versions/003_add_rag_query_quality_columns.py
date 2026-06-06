"""Add reliability/quality columns to rag_queries

Revision ID: 003
Revises: 002
Create Date: 2026-05-28

"""
from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "003"
down_revision: str | None = "002"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "rag_queries",
        sa.Column("hallucination_risk", sa.Float, nullable=False, server_default="0"),
    )
    op.add_column(
        "rag_queries",
        sa.Column("citation_coverage", sa.Float, nullable=False, server_default="0"),
    )
    op.add_column(
        "rag_queries",
        sa.Column("retrieval_precision", sa.Float, nullable=False, server_default="0"),
    )
    op.add_column(
        "rag_queries",
        sa.Column("answer_completeness", sa.Float, nullable=False, server_default="0"),
    )
    op.add_column("rag_queries", sa.Column("product_area", sa.String(200), nullable=True))
    op.add_column(
        "rag_queries",
        sa.Column("provider", sa.String(100), nullable=False, server_default=""),
    )
    op.add_column(
        "rag_queries",
        sa.Column("model", sa.String(200), nullable=False, server_default=""),
    )
    op.add_column(
        "rag_queries",
        sa.Column("is_fallback", sa.Boolean, nullable=False, server_default=sa.false()),
    )
    op.add_column("rag_queries", sa.Column("feedback", sa.String(50), nullable=True))


def downgrade() -> None:
    for col in (
        "feedback",
        "is_fallback",
        "model",
        "provider",
        "product_area",
        "answer_completeness",
        "retrieval_precision",
        "citation_coverage",
        "hallucination_risk",
    ):
        op.drop_column("rag_queries", col)
