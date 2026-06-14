"""V7 tool registry: defines built-in mock tools and manages tool CRUD."""
import json
import uuid

from sqlalchemy.orm import Session

from app.models.models import Tool

# ---------------------------------------------------------------------------
# Built-in tool definitions
# ---------------------------------------------------------------------------

BUILTIN_TOOLS = [
    {
        "name": "Create Ticket",
        "slug": "create_ticket",
        "description": (
            "Creates a new support ticket in the system. Use this when a "
            "customer reports a new issue that needs tracking."
        ),
        "handler": "create_ticket",
        "category": "tickets",
        "parameters_schema": {
            "type": "object",
            "properties": {
                "title": {"type": "string", "description": "Ticket title"},
                "body": {"type": "string", "description": "Ticket description"},
                "product_area": {
                    "type": "string",
                    "description": "Product area",
                    "enum": ["billing", "api", "dashboard", "mobile", "integrations", "other"],
                },
                "issue_type": {
                    "type": "string",
                    "description": "Issue type",
                    "enum": ["bug", "feature_request", "question", "incident", "other"],
                },
                "priority": {
                    "type": "string",
                    "description": "Priority level",
                    "enum": ["critical", "high", "medium", "low"],
                },
                "customer_email": {"type": "string", "description": "Customer email"},
            },
            "required": ["title", "body"],
        },
    },
    {
        "name": "Update Ticket Status",
        "slug": "update_ticket_status",
        "description": (
            "Updates the status of an existing ticket. Use this to move tickets "
            "through the workflow (open, in_progress, resolved, closed)."
        ),
        "handler": "update_ticket_status",
        "category": "tickets",
        "parameters_schema": {
            "type": "object",
            "properties": {
                "ticket_id": {"type": "string", "description": "Ticket ID to update"},
                "status": {
                    "type": "string",
                    "description": "New status",
                    "enum": ["open", "in_progress", "resolved", "closed"],
                },
                "resolution": {"type": "string", "description": "Resolution notes"},
            },
            "required": ["ticket_id", "status"],
        },
    },
    {
        "name": "Lookup Customer",
        "slug": "lookup_customer",
        "description": (
            "Looks up customer information by email or name. Returns customer "
            "profile, tier, conversation history, and unresolved issues."
        ),
        "handler": "lookup_customer",
        "category": "customers",
        "parameters_schema": {
            "type": "object",
            "properties": {
                "email": {"type": "string", "description": "Customer email"},
                "name": {"type": "string", "description": "Customer name"},
            },
        },
    },
    {
        "name": "Search Knowledge Base",
        "slug": "search_knowledge_base",
        "description": (
            "Searches the knowledge base for articles matching a query. "
            "Returns relevant articles with resolution steps."
        ),
        "handler": "search_knowledge_base",
        "category": "knowledge",
        "parameters_schema": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Search query"},
                "product_area": {"type": "string", "description": "Filter by product area"},
            },
            "required": ["query"],
        },
    },
    {
        "name": "Check SLA Status",
        "slug": "check_sla_status",
        "description": (
            "Checks SLA risk status for open tickets. Returns tickets at risk "
            "of breaching their SLA commitments."
        ),
        "handler": "check_sla_status",
        "category": "operations",
        "parameters_schema": {
            "type": "object",
            "properties": {
                "ticket_id": {
                    "type": "string",
                    "description": "Specific ticket ID to check (optional)",
                },
            },
        },
    },
    {
        "name": "List Conversation Handoffs",
        "slug": "list_handoffs",
        "description": (
            "Lists pending human handoffs that need attention. Use this to "
            "check if there are customers waiting for human support."
        ),
        "handler": "list_handoffs",
        "category": "operations",
        "parameters_schema": {
            "type": "object",
            "properties": {
                "status": {
                    "type": "string",
                    "description": "Filter by status",
                    "enum": ["pending", "acknowledged", "resolved"],
                },
            },
        },
    },
]


def get_builtin_tool_definitions() -> list[dict]:
    return BUILTIN_TOOLS


def get_builtin_tool_by_slug(slug: str) -> dict | None:
    for t in BUILTIN_TOOLS:
        if t["slug"] == slug:
            return t
    return None


def upsert_builtin_tools(db: Session, workspace_id) -> int:
    """Ensure all built-in tools exist for this workspace. Returns count of newly created tools."""
    created = 0
    for defn in BUILTIN_TOOLS:
        existing = (
            db.query(Tool)
            .filter(Tool.workspace_id == workspace_id, Tool.slug == defn["slug"])
            .first()
        )
        if not existing:
            tool = Tool(
                id=uuid.uuid4(),
                workspace_id=workspace_id,
                name=defn["name"],
                slug=defn["slug"],
                description=defn["description"],
                handler=defn["handler"],
                parameters_schema_json=json.dumps(defn["parameters_schema"]),
                category=defn["category"],
                enabled=True,
            )
            db.add(tool)
            created += 1
    if created:
        db.flush()
    return created


def list_tools(db: Session, workspace_id, enabled_only: bool = False) -> list[Tool]:
    query = db.query(Tool).filter(Tool.workspace_id == workspace_id)
    if enabled_only:
        query = query.filter(Tool.enabled.is_(True))
    return query.order_by(Tool.name).all()


def get_tool(db: Session, workspace_id, tool_id: uuid.UUID) -> Tool | None:
    return (
        db.query(Tool)
        .filter(Tool.id == tool_id, Tool.workspace_id == workspace_id)
        .first()
    )


def get_tool_by_slug(db: Session, workspace_id, slug: str) -> Tool | None:
    return (
        db.query(Tool)
        .filter(Tool.slug == slug, Tool.workspace_id == workspace_id)
        .first()
    )
