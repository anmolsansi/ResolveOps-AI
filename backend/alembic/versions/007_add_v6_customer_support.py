"""Add V6 customer-facing support tables: customer_profiles, conversations,
conversation_messages, human_handoffs, resolution_outcomes.

Revision ID: 007
Revises: 006
Create Date: 2026-06-14

"""
from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID

from alembic import op

revision: str = "007"
down_revision: str | None = "006"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "customer_profiles",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("workspace_id", UUID(as_uuid=True), sa.ForeignKey("workspaces.id"), nullable=True),
        sa.Column("external_id", sa.String(320), nullable=False),
        sa.Column("name", sa.String(200), nullable=True),
        sa.Column("email", sa.String(320), nullable=True),
        sa.Column("company", sa.String(200), nullable=True),
        sa.Column("customer_tier", sa.String(100), nullable=False, server_default="free"),
        sa.Column("sentiment_score", sa.Float, nullable=False, server_default="0.0"),
        sa.Column("total_conversations", sa.Integer, nullable=False, server_default="0"),
        sa.Column("unresolved_issues", sa.Integer, nullable=False, server_default="0"),
        sa.Column("last_seen_at", sa.DateTime, nullable=True),
        sa.Column("created_at", sa.DateTime, server_default=sa.func.now()),
    )
    op.create_index("ix_customer_profiles_external_id", "customer_profiles", ["external_id"])
    op.create_index("ix_customer_profiles_workspace_id", "customer_profiles", ["workspace_id"])

    op.create_table(
        "conversations",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("workspace_id", UUID(as_uuid=True), sa.ForeignKey("workspaces.id"), nullable=True),
        sa.Column("customer_id", UUID(as_uuid=True), sa.ForeignKey("customer_profiles.id"), nullable=False),
        sa.Column("channel", sa.String(50), nullable=False, server_default="widget"),
        sa.Column("status", sa.String(50), nullable=False, server_default="open"),
        sa.Column("subject", sa.String(500), nullable=True),
        sa.Column("product_area", sa.String(200), nullable=True),
        sa.Column("assigned_agent_id", UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("sentiment", sa.String(50), nullable=True),
        sa.Column("ai_resolution_outcome", sa.String(50), nullable=True),
        sa.Column("resolution_summary", sa.Text, nullable=True),
        sa.Column("started_at", sa.DateTime, server_default=sa.func.now()),
        sa.Column("last_message_at", sa.DateTime, server_default=sa.func.now()),
        sa.Column("resolved_at", sa.DateTime, nullable=True),
        sa.Column("created_at", sa.DateTime, server_default=sa.func.now()),
    )
    op.create_index("ix_conversations_status", "conversations", ["status"])
    op.create_index("ix_conversations_customer_id", "conversations", ["customer_id"])
    op.create_index("ix_conversations_workspace_id", "conversations", ["workspace_id"])

    op.create_table(
        "conversation_messages",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("conversation_id", UUID(as_uuid=True), sa.ForeignKey("conversations.id"), nullable=False),
        sa.Column("role", sa.String(50), nullable=False),
        sa.Column("content", sa.Text, nullable=False),
        sa.Column("citations_json", sa.Text, nullable=True),
        sa.Column("confidence", sa.Float, nullable=True),
        sa.Column("is_escalation_trigger", sa.Boolean, nullable=False, server_default=sa.false()),
        sa.Column("metadata_json", sa.Text, nullable=True),
        sa.Column("created_at", sa.DateTime, server_default=sa.func.now()),
    )
    op.create_index("ix_conversation_messages_conversation_id", "conversation_messages", ["conversation_id"])

    op.create_table(
        "human_handoffs",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("conversation_id", UUID(as_uuid=True), sa.ForeignKey("conversations.id"), nullable=False),
        sa.Column("workspace_id", UUID(as_uuid=True), sa.ForeignKey("workspaces.id"), nullable=True),
        sa.Column("trigger_reason", sa.String(100), nullable=False),
        sa.Column("summary", sa.Text, nullable=False),
        sa.Column("likely_intent", sa.String(500), nullable=False),
        sa.Column("customer_profile_snapshot", sa.Text, nullable=False),
        sa.Column("cited_docs_json", sa.Text, nullable=True),
        sa.Column("suggested_reply", sa.Text, nullable=True),
        sa.Column("status", sa.String(50), nullable=False, server_default="pending"),
        sa.Column("assigned_to", UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("created_at", sa.DateTime, server_default=sa.func.now()),
        sa.Column("resolved_at", sa.DateTime, nullable=True),
    )
    op.create_index("ix_human_handoffs_conversation_id", "human_handoffs", ["conversation_id"])
    op.create_index("ix_human_handoffs_status", "human_handoffs", ["status"])
    op.create_index("ix_human_handoffs_workspace_id", "human_handoffs", ["workspace_id"])

    op.create_table(
        "resolution_outcomes",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("conversation_id", UUID(as_uuid=True), sa.ForeignKey("conversations.id"), nullable=False),
        sa.Column("workspace_id", UUID(as_uuid=True), sa.ForeignKey("workspaces.id"), nullable=True),
        sa.Column("outcome", sa.String(50), nullable=False),
        sa.Column("confidence_at_resolution", sa.Float, nullable=False, server_default="0.0"),
        sa.Column("total_messages", sa.Integer, nullable=False, server_default="0"),
        sa.Column("ai_message_count", sa.Integer, nullable=False, server_default="0"),
        sa.Column("human_message_count", sa.Integer, nullable=False, server_default="0"),
        sa.Column("time_to_resolution_seconds", sa.Integer, nullable=True),
        sa.Column("customer_satisfaction", sa.String(50), nullable=True),
        sa.Column("notes", sa.Text, nullable=True),
        sa.Column("created_at", sa.DateTime, server_default=sa.func.now()),
    )
    op.create_index("ix_resolution_outcomes_conversation_id", "resolution_outcomes", ["conversation_id"])
    op.create_index("ix_resolution_outcomes_workspace_id", "resolution_outcomes", ["workspace_id"])


def downgrade() -> None:
    op.drop_index("ix_resolution_outcomes_workspace_id", table_name="resolution_outcomes")
    op.drop_index("ix_resolution_outcomes_conversation_id", table_name="resolution_outcomes")
    op.drop_table("resolution_outcomes")

    op.drop_index("ix_human_handoffs_workspace_id", table_name="human_handoffs")
    op.drop_index("ix_human_handoffs_status", table_name="human_handoffs")
    op.drop_index("ix_human_handoffs_conversation_id", table_name="human_handoffs")
    op.drop_table("human_handoffs")

    op.drop_index("ix_conversation_messages_conversation_id", table_name="conversation_messages")
    op.drop_table("conversation_messages")

    op.drop_index("ix_conversations_workspace_id", table_name="conversations")
    op.drop_index("ix_conversations_customer_id", table_name="conversations")
    op.drop_index("ix_conversations_status", table_name="conversations")
    op.drop_table("conversations")

    op.drop_index("ix_customer_profiles_workspace_id", table_name="customer_profiles")
    op.drop_index("ix_customer_profiles_external_id", table_name="customer_profiles")
    op.drop_table("customer_profiles")
