"""Add V7 action-taking agent workflow tables: tools, tool_executions,
action_logs.

Revision ID: 008
Revises: 007
Create Date: 2026-06-14

"""
from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID

from alembic import op

revision: str = "008"
down_revision: str | None = "007"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "tools",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("workspace_id", UUID(as_uuid=True), sa.ForeignKey("workspaces.id"), nullable=True),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("slug", sa.String(200), nullable=False),
        sa.Column("description", sa.Text, nullable=False),
        sa.Column("handler", sa.String(200), nullable=False),
        sa.Column("parameters_schema_json", sa.Text, nullable=False, server_default="{}"),
        sa.Column("enabled", sa.Boolean, nullable=False, server_default=sa.true()),
        sa.Column("category", sa.String(100), nullable=False, server_default="general"),
        sa.Column("created_at", sa.DateTime, server_default=sa.func.now()),
    )
    op.create_index("ix_tools_workspace_id", "tools", ["workspace_id"])
    op.create_index("ix_tools_workspace_slug", "tools", ["workspace_id", "slug"], unique=True)

    op.create_table(
        "tool_executions",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("tool_id", UUID(as_uuid=True), sa.ForeignKey("tools.id"), nullable=False),
        sa.Column("workspace_id", UUID(as_uuid=True), sa.ForeignKey("workspaces.id"), nullable=True),
        sa.Column("input_json", sa.Text, nullable=False, server_default="{}"),
        sa.Column("output_json", sa.Text, nullable=True),
        sa.Column("status", sa.String(20), nullable=False, server_default="pending"),
        sa.Column("error", sa.Text, nullable=True),
        sa.Column("latency_ms", sa.Integer, nullable=True),
        sa.Column("conversation_id", UUID(as_uuid=True), sa.ForeignKey("conversations.id"), nullable=True),
        sa.Column("triggered_by", sa.String(50), nullable=False, server_default="ai"),
        sa.Column("created_at", sa.DateTime, server_default=sa.func.now()),
    )
    op.create_index("ix_tool_executions_tool_id", "tool_executions", ["tool_id"])
    op.create_index("ix_tool_executions_workspace_id", "tool_executions", ["workspace_id"])
    op.create_index("ix_tool_executions_status", "tool_executions", ["status"])
    op.create_index("ix_tool_executions_created_at", "tool_executions", ["created_at"])

    op.create_table(
        "action_logs",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("workspace_id", UUID(as_uuid=True), sa.ForeignKey("workspaces.id"), nullable=True),
        sa.Column("action_type", sa.String(100), nullable=False),
        sa.Column("resource_type", sa.String(100), nullable=False),
        sa.Column("resource_id", sa.String(200), nullable=True),
        sa.Column("tool_execution_id", UUID(as_uuid=True), sa.ForeignKey("tool_executions.id"), nullable=True),
        sa.Column("detail", sa.Text, nullable=True),
        sa.Column("actor", sa.String(100), nullable=False, server_default="ai_agent"),
        sa.Column("created_at", sa.DateTime, server_default=sa.func.now()),
    )
    op.create_index("ix_action_logs_workspace_id", "action_logs", ["workspace_id"])
    op.create_index("ix_action_logs_action_type", "action_logs", ["action_type"])
    op.create_index("ix_action_logs_created_at", "action_logs", ["created_at"])


def downgrade() -> None:
    op.drop_index("ix_action_logs_created_at", table_name="action_logs")
    op.drop_index("ix_action_logs_action_type", table_name="action_logs")
    op.drop_index("ix_action_logs_workspace_id", table_name="action_logs")
    op.drop_table("action_logs")

    op.drop_index("ix_tool_executions_created_at", table_name="tool_executions")
    op.drop_index("ix_tool_executions_status", table_name="tool_executions")
    op.drop_index("ix_tool_executions_workspace_id", table_name="tool_executions")
    op.drop_index("ix_tool_executions_tool_id", table_name="tool_executions")
    op.drop_table("tool_executions")

    op.drop_index("ix_tools_workspace_slug", table_name="tools")
    op.drop_index("ix_tools_workspace_id", table_name="tools")
    op.drop_table("tools")
