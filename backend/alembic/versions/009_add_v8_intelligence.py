"""Add V8 agent intelligence tables: conversation_summaries, kb_suggestions,
copilot_suggestions.

Revision ID: 009
Revises: 008
Create Date: 2026-06-15

"""
from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID

from alembic import op

revision: str = "009"
down_revision: str | None = "008"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "conversation_summaries",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("conversation_id", UUID(as_uuid=True), sa.ForeignKey("conversations.id"), nullable=False),
        sa.Column("workspace_id", UUID(as_uuid=True), sa.ForeignKey("workspaces.id"), nullable=True),
        sa.Column("summary", sa.Text, nullable=False),
        sa.Column("resolution_steps", sa.Text, nullable=True),
        sa.Column("key_topics_json", sa.Text, nullable=True),
        sa.Column("sentiment_at_resolution", sa.String(50), nullable=True),
        sa.Column("created_at", sa.DateTime, server_default=sa.func.now()),
    )
    op.create_index("ix_conv_summaries_conversation_id", "conversation_summaries", ["conversation_id"])
    op.create_index("ix_conv_summaries_workspace_id", "conversation_summaries", ["workspace_id"])

    op.create_table(
        "kb_suggestions",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("workspace_id", UUID(as_uuid=True), sa.ForeignKey("workspaces.id"), nullable=True),
        sa.Column("suggested_title", sa.String(500), nullable=False),
        sa.Column("suggested_content", sa.Text, nullable=False),
        sa.Column("product_area", sa.String(200), nullable=True),
        sa.Column("issue_type", sa.String(200), nullable=True),
        sa.Column("source_conversation_ids_json", sa.Text, nullable=False, server_default="[]"),
        sa.Column("occurrence_count", sa.Integer, nullable=False, server_default="1"),
        sa.Column("status", sa.String(50), nullable=False, server_default="pending"),
        sa.Column("created_at", sa.DateTime, server_default=sa.func.now()),
    )
    op.create_index("ix_kb_suggestions_workspace_id", "kb_suggestions", ["workspace_id"])
    op.create_index("ix_kb_suggestions_status", "kb_suggestions", ["status"])

    op.create_table(
        "copilot_suggestions",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("workspace_id", UUID(as_uuid=True), sa.ForeignKey("workspaces.id"), nullable=True),
        sa.Column("conversation_id", UUID(as_uuid=True), sa.ForeignKey("conversations.id"), nullable=True),
        sa.Column("suggestion_type", sa.String(100), nullable=False),
        sa.Column("title", sa.String(500), nullable=False),
        sa.Column("content", sa.Text, nullable=False),
        sa.Column("confidence", sa.Float, nullable=False, server_default="0.0"),
        sa.Column("status", sa.String(50), nullable=False, server_default="pending"),
        sa.Column("created_at", sa.DateTime, server_default=sa.func.now()),
    )
    op.create_index("ix_copilot_suggestions_workspace_id", "copilot_suggestions", ["workspace_id"])
    op.create_index("ix_copilot_suggestions_suggestion_type", "copilot_suggestions", ["suggestion_type"])
    op.create_index("ix_copilot_suggestions_created_at", "copilot_suggestions", ["created_at"])


def downgrade() -> None:
    op.drop_index("ix_copilot_suggestions_created_at", table_name="copilot_suggestions")
    op.drop_index("ix_copilot_suggestions_suggestion_type", table_name="copilot_suggestions")
    op.drop_index("ix_copilot_suggestions_workspace_id", table_name="copilot_suggestions")
    op.drop_table("copilot_suggestions")

    op.drop_index("ix_kb_suggestions_status", table_name="kb_suggestions")
    op.drop_index("ix_kb_suggestions_workspace_id", table_name="kb_suggestions")
    op.drop_table("kb_suggestions")

    op.drop_index("ix_conv_summaries_workspace_id", table_name="conversation_summaries")
    op.drop_index("ix_conv_summaries_conversation_id", table_name="conversation_summaries")
    op.drop_table("conversation_summaries")
