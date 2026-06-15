"""Add V9 workflow automation tables: routing_rules, canned_responses,
portal_articles.

Revision ID: 010
Revises: 009
Create Date: 2026-06-15

"""
from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID

from alembic import op

revision: str = "010"
down_revision: str | None = "009"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "routing_rules",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("workspace_id", UUID(as_uuid=True), sa.ForeignKey("workspaces.id"), nullable=True),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("priority", sa.Integer, nullable=False, server_default="0"),
        sa.Column("enabled", sa.Boolean, nullable=False, server_default=sa.true()),
        sa.Column("conditions_json", sa.Text, nullable=False, server_default="{}"),
        sa.Column("actions_json", sa.Text, nullable=False, server_default="{}"),
        sa.Column("match_count", sa.Integer, nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime, server_default=sa.func.now()),
    )
    op.create_index("ix_routing_rules_workspace_id", "routing_rules", ["workspace_id"])

    op.create_table(
        "canned_responses",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("workspace_id", UUID(as_uuid=True), sa.ForeignKey("workspaces.id"), nullable=True),
        sa.Column("title", sa.String(300), nullable=False),
        sa.Column("content", sa.Text, nullable=False),
        sa.Column("category", sa.String(100), nullable=False, server_default="general"),
        sa.Column("shortcut", sa.String(50), nullable=True),
        sa.Column("usage_count", sa.Integer, nullable=False, server_default="0"),
        sa.Column("enabled", sa.Boolean, nullable=False, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime, server_default=sa.func.now()),
    )
    op.create_index("ix_canned_responses_workspace_id", "canned_responses", ["workspace_id"])

    op.create_table(
        "portal_articles",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("workspace_id", UUID(as_uuid=True), sa.ForeignKey("workspaces.id"), nullable=True),
        sa.Column("title", sa.String(500), nullable=False),
        sa.Column("slug", sa.String(500), nullable=False),
        sa.Column("content", sa.Text, nullable=False),
        sa.Column("category", sa.String(100), nullable=False, server_default="general"),
        sa.Column("product_area", sa.String(200), nullable=True),
        sa.Column("tags_json", sa.Text, nullable=False, server_default="[]"),
        sa.Column("published", sa.Boolean, nullable=False, server_default=sa.false()),
        sa.Column("view_count", sa.Integer, nullable=False, server_default="0"),
        sa.Column("helpful_count", sa.Integer, nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime, server_default=sa.func.now()),
    )
    op.create_index("ix_portal_articles_workspace_id", "portal_articles", ["workspace_id"])
    op.create_index(
        "ix_portal_articles_workspace_slug",
        "portal_articles",
        ["workspace_id", "slug"],
        unique=True,
    )


def downgrade() -> None:
    op.drop_index("ix_portal_articles_workspace_slug", table_name="portal_articles")
    op.drop_index("ix_portal_articles_workspace_id", table_name="portal_articles")
    op.drop_table("portal_articles")

    op.drop_index("ix_canned_responses_workspace_id", table_name="canned_responses")
    op.drop_table("canned_responses")

    op.drop_index("ix_routing_rules_workspace_id", table_name="routing_rules")
    op.drop_table("routing_rules")
