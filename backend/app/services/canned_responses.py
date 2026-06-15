"""V9 canned responses service: CRUD and usage tracking for response
templates."""
import uuid

from sqlalchemy.orm import Session

from app.models.models import CannedResponse


def list_canned_responses(
    db: Session, workspace_id, category: str | None = None,
) -> list[dict]:
    query = db.query(CannedResponse).filter(
        CannedResponse.workspace_id == workspace_id,
    )
    if category:
        query = query.filter(CannedResponse.category == category)
    items = query.order_by(CannedResponse.usage_count.desc()).all()
    return [_to_dict(c) for c in items]


def get_canned_response(db: Session, response_id, workspace_id) -> dict | None:
    c = db.query(CannedResponse).filter(
        CannedResponse.id == response_id,
        CannedResponse.workspace_id == workspace_id,
    ).first()
    return _to_dict(c) if c else None


def create_canned_response(
    db: Session, workspace_id, title: str, content: str,
    category: str, shortcut: str | None,
) -> dict:
    c = CannedResponse(
        id=uuid.uuid4(),
        workspace_id=workspace_id,
        title=title,
        content=content,
        category=category,
        shortcut=shortcut,
    )
    db.add(c)
    db.flush()
    return _to_dict(c)


def update_canned_response(
    db: Session, response_id, workspace_id, **kwargs,
) -> dict | None:
    c = db.query(CannedResponse).filter(
        CannedResponse.id == response_id,
        CannedResponse.workspace_id == workspace_id,
    ).first()
    if not c:
        return None
    for field in ("title", "content", "category", "shortcut", "enabled"):
        if field in kwargs and kwargs[field] is not None:
            setattr(c, field, kwargs[field])
    db.flush()
    return _to_dict(c)


def delete_canned_response(db: Session, response_id, workspace_id) -> bool:
    c = db.query(CannedResponse).filter(
        CannedResponse.id == response_id,
        CannedResponse.workspace_id == workspace_id,
    ).first()
    if not c:
        return False
    db.delete(c)
    db.flush()
    return True


def use_canned_response(db: Session, response_id, workspace_id) -> dict | None:
    """Increment usage count and return the response."""
    c = db.query(CannedResponse).filter(
        CannedResponse.id == response_id,
        CannedResponse.workspace_id == workspace_id,
    ).first()
    if not c:
        return None
    c.usage_count += 1
    db.flush()
    return _to_dict(c)


def search_canned_responses(
    db: Session, workspace_id, query: str,
) -> list[dict]:
    q = db.query(CannedResponse).filter(
        CannedResponse.workspace_id == workspace_id,
        CannedResponse.enabled.is_(True),
    )
    lower = query.lower()
    items = q.all()
    matches = [
        c for c in items
        if lower in c.title.lower() or lower in c.content.lower()
        or (c.shortcut and lower in c.shortcut.lower())
    ]
    matches.sort(key=lambda c: c.usage_count, reverse=True)
    return [_to_dict(c) for c in matches[:20]]


def _to_dict(c: CannedResponse) -> dict:
    return {
        "id": str(c.id),
        "title": c.title,
        "content": c.content,
        "category": c.category,
        "shortcut": c.shortcut,
        "usage_count": c.usage_count,
        "enabled": c.enabled,
        "created_at": c.created_at.isoformat() if c.created_at else "",
        "updated_at": c.updated_at.isoformat() if c.updated_at else "",
    }
