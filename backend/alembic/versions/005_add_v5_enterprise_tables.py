"""Add V5 enterprise tables: users, workspaces, memberships, audit_logs,
app_settings, prompt_templates, background_jobs.

Also adds a pgvector embedding column on ticket_chunks when running on
PostgreSQL with the vector extension available (no-op on SQLite).

Revision ID: 005
Revises: 004
Create Date: 2026-05-28

"""
from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID

from alembic import op

revision: str = "005"
down_revision: str | None = "004"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("email", sa.String(320), nullable=False),
        sa.Column("password_hash", sa.String(255), nullable=False),
        sa.Column("role", sa.String(20), nullable=False, server_default="member"),
        sa.Column("is_active", sa.Boolean, nullable=False, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime, server_default=sa.func.now()),
    )
    op.create_index("ix_users_email", "users", ["email"], unique=True)

    op.create_table(
        "workspaces",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("slug", sa.String(200), nullable=False),
        sa.Column("created_at", sa.DateTime, server_default=sa.func.now()),
    )
    op.create_index("ix_workspaces_slug", "workspaces", ["slug"], unique=True)

    op.create_table(
        "memberships",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "workspace_id", UUID(as_uuid=True), sa.ForeignKey("workspaces.id"), nullable=False
        ),
        sa.Column("user_id", UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("role", sa.String(20), nullable=False, server_default="member"),
        sa.Column("created_at", sa.DateTime, server_default=sa.func.now()),
    )
    op.create_index(
        "ix_memberships_workspace_user",
        "memberships",
        ["workspace_id", "user_id"],
        unique=True,
    )

    op.create_table(
        "audit_logs",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("actor_email", sa.String(320), server_default="system"),
        sa.Column("action", sa.String(100), nullable=False),
        sa.Column("resource_type", sa.String(100), server_default=""),
        sa.Column("resource_id", sa.String(200), nullable=True),
        sa.Column("workspace_id", UUID(as_uuid=True), nullable=True),
        sa.Column("detail", sa.Text, nullable=True),
        sa.Column("ip_address", sa.String(64), nullable=True),
        sa.Column("created_at", sa.DateTime, server_default=sa.func.now()),
    )
    op.create_index("ix_audit_logs_created_at", "audit_logs", ["created_at"])
    op.create_index("ix_audit_logs_action", "audit_logs", ["action"])

    op.create_table(
        "app_settings",
        sa.Column("key", sa.String(100), primary_key=True),
        sa.Column("value", sa.Text, nullable=False),
        sa.Column("updated_at", sa.DateTime, server_default=sa.func.now()),
    )

    op.create_table(
        "prompt_templates",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("version", sa.Integer, nullable=False, server_default="1"),
        sa.Column("content", sa.Text, nullable=False),
        sa.Column("is_active", sa.Boolean, nullable=False, server_default=sa.false()),
        sa.Column("created_at", sa.DateTime, server_default=sa.func.now()),
    )
    op.create_index(
        "ix_prompt_templates_name_version",
        "prompt_templates",
        ["name", "version"],
        unique=True,
    )

    op.create_table(
        "background_jobs",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("job_type", sa.String(50), nullable=False),
        sa.Column("status", sa.String(20), nullable=False, server_default="pending"),
        sa.Column("payload_json", sa.Text, nullable=True),
        sa.Column("result_json", sa.Text, nullable=True),
        sa.Column("error", sa.Text, nullable=True),
        sa.Column("attempts", sa.Integer, nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime, server_default=sa.func.now()),
        sa.Column("started_at", sa.DateTime, nullable=True),
        sa.Column("finished_at", sa.DateTime, nullable=True),
    )
    op.create_index("ix_background_jobs_status", "background_jobs", ["status"])
    op.create_index("ix_background_jobs_created_at", "background_jobs", ["created_at"])

    # pgvector-backed retrieval: only on PostgreSQL where the extension is
    # actually installable. We must check availability up front rather than
    # rely on try/except — a failed CREATE EXTENSION aborts the surrounding
    # (transactional DDL) migration transaction, which would then fail the
    # alembic_version update. The JSON-array fallback is used when absent.
    bind = op.get_bind()
    if bind.dialect.name == "postgresql":
        available = bind.execute(
            sa.text("SELECT 1 FROM pg_available_extensions WHERE name = 'vector'")
        ).first()
        if available is not None:
            op.execute("CREATE EXTENSION IF NOT EXISTS vector")
            op.execute("ALTER TABLE ticket_chunks ADD COLUMN IF NOT EXISTS embedding_vec vector")


def downgrade() -> None:
    bind = op.get_bind()
    if bind.dialect.name == "postgresql":
        op.execute("ALTER TABLE ticket_chunks DROP COLUMN IF EXISTS embedding_vec")

    op.drop_index("ix_background_jobs_created_at", table_name="background_jobs")
    op.drop_index("ix_background_jobs_status", table_name="background_jobs")
    op.drop_table("background_jobs")
    op.drop_index("ix_prompt_templates_name_version", table_name="prompt_templates")
    op.drop_table("prompt_templates")
    op.drop_table("app_settings")
    op.drop_index("ix_audit_logs_action", table_name="audit_logs")
    op.drop_index("ix_audit_logs_created_at", table_name="audit_logs")
    op.drop_table("audit_logs")
    op.drop_index("ix_memberships_workspace_user", table_name="memberships")
    op.drop_table("memberships")
    op.drop_index("ix_workspaces_slug", table_name="workspaces")
    op.drop_table("workspaces")
    op.drop_index("ix_users_email", table_name="users")
    op.drop_table("users")
