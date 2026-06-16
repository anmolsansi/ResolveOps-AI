"""011 add v10a analytics and security."""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID

revision = "011"
down_revision = "010"


def upgrade() -> None:
    op.create_table(
        "saved_reports",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("workspace_id", UUID(as_uuid=True), sa.ForeignKey("workspaces.id"), nullable=True, index=True),
        sa.Column("name", sa.String(300), nullable=False),
        sa.Column("report_type", sa.String(50), nullable=False),
        sa.Column("filters_json", sa.Text, server_default="{}"),
        sa.Column("created_by", sa.String(200), server_default=""),
        sa.Column("created_at", sa.DateTime, server_default=sa.func.now()),
    )

    op.create_table(
        "export_jobs",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("workspace_id", UUID(as_uuid=True), sa.ForeignKey("workspaces.id"), nullable=True, index=True),
        sa.Column("report_type", sa.String(50), nullable=False),
        sa.Column("filters_json", sa.Text, server_default="{}"),
        sa.Column("status", sa.String(20), server_default="pending"),
        sa.Column("file_path", sa.String(500), nullable=True),
        sa.Column("row_count", sa.Integer, server_default="0"),
        sa.Column("created_by", sa.String(200), server_default=""),
        sa.Column("created_at", sa.DateTime, server_default=sa.func.now()),
        sa.Column("completed_at", sa.DateTime, nullable=True),
    )

    op.create_table(
        "api_keys",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("workspace_id", UUID(as_uuid=True), sa.ForeignKey("workspaces.id"), nullable=True, index=True),
        sa.Column("user_id", UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=True, index=True),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("key_prefix", sa.String(20), nullable=False, index=True),
        sa.Column("key_hash", sa.String(200), nullable=False, index=True),
        sa.Column("scopes_json", sa.Text, server_default="[]"),
        sa.Column("expires_at", sa.DateTime, nullable=True),
        sa.Column("last_used_at", sa.DateTime, nullable=True),
        sa.Column("enabled", sa.Boolean, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime, server_default=sa.func.now()),
    )

    op.create_table(
        "login_attempts",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("email", sa.String(200), nullable=False, index=True),
        sa.Column("ip_address", sa.String(50), server_default=""),
        sa.Column("success", sa.Boolean, server_default=sa.false()),
        sa.Column("created_at", sa.DateTime, server_default=sa.func.now()),
    )

    op.create_table(
        "ip_allowlist",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("workspace_id", UUID(as_uuid=True), sa.ForeignKey("workspaces.id"), nullable=True, index=True),
        sa.Column("ip_address", sa.String(50), nullable=False),
        sa.Column("note", sa.String(300), server_default=""),
        sa.Column("enabled", sa.Boolean, server_default=sa.true()),
        sa.Column("created_by", sa.String(200), server_default=""),
        sa.Column("created_at", sa.DateTime, server_default=sa.func.now()),
    )
    op.create_index("ix_ip_allowlist_workspace_ip", "ip_allowlist", ["workspace_id", "ip_address"], unique=True)

    op.create_table(
        "security_settings",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("workspace_id", UUID(as_uuid=True), sa.ForeignKey("workspaces.id"), nullable=True, index=True, unique=True),
        sa.Column("rate_limit_requests_per_minute", sa.Integer, server_default="60"),
        sa.Column("rate_limit_burst", sa.Integer, server_default="10"),
        sa.Column("max_login_attempts", sa.Integer, server_default="5"),
        sa.Column("lockout_duration_minutes", sa.Integer, server_default="15"),
        sa.Column("session_timeout_minutes", sa.Integer, server_default="480"),
        sa.Column("ip_allowlist_enabled", sa.Boolean, server_default=sa.false()),
        sa.Column("created_at", sa.DateTime, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime, server_default=sa.func.now()),
    )

    op.create_table(
        "rate_limit_logs",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("key", sa.String(200), nullable=False, index=True),
        sa.Column("endpoint", sa.String(200), server_default=""),
        sa.Column("timestamp", sa.DateTime, server_default=sa.func.now(), index=True),
    )


def downgrade() -> None:
    op.drop_table("rate_limit_logs")
    op.drop_table("security_settings")
    op.drop_index("ix_ip_allowlist_workspace_ip", table_name="ip_allowlist")
    op.drop_table("ip_allowlist")
    op.drop_table("login_attempts")
    op.drop_table("api_keys")
    op.drop_table("export_jobs")
    op.drop_table("saved_reports")
