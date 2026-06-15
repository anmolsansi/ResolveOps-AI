"""V9 portal service: public knowledge base articles and ticket status
lookup for the self-service portal."""
import json
import re
import uuid

from sqlalchemy.orm import Session

from app.models.models import Conversation, CustomerProfile, PortalArticle


def _slugify(text: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")
    return slug or "article"


def list_portal_articles(
    db: Session, workspace_id, published_only: bool = True,
) -> list[dict]:
    query = db.query(PortalArticle).filter(
        PortalArticle.workspace_id == workspace_id,
    )
    if published_only:
        query = query.filter(PortalArticle.published.is_(True))
    items = query.order_by(PortalArticle.title).all()
    return [_article_to_dict(a) for a in items]


def get_portal_article(db: Session, article_id, workspace_id) -> dict | None:
    a = db.query(PortalArticle).filter(
        PortalArticle.id == article_id,
        PortalArticle.workspace_id == workspace_id,
    ).first()
    return _article_to_dict(a) if a else None


def get_portal_article_by_slug(
    db: Session, slug: str, workspace_id,
) -> dict | None:
    a = db.query(PortalArticle).filter(
        PortalArticle.slug == slug,
        PortalArticle.workspace_id == workspace_id,
    ).first()
    if not a:
        return None
    a.view_count += 1
    db.flush()
    return _article_to_dict(a)


def create_portal_article(
    db: Session, workspace_id, title: str, content: str,
    category: str, product_area: str | None, tags: list[str],
    published: bool,
) -> dict:
    slug = _slugify(title)
    existing = db.query(PortalArticle).filter(
        PortalArticle.slug == slug,
        PortalArticle.workspace_id == workspace_id,
    ).first()
    if existing:
        slug = f"{slug}-{uuid.uuid4().hex[:6]}"

    a = PortalArticle(
        id=uuid.uuid4(),
        workspace_id=workspace_id,
        title=title,
        slug=slug,
        content=content,
        category=category,
        product_area=product_area,
        tags_json=json.dumps(tags),
        published=published,
    )
    db.add(a)
    db.flush()
    return _article_to_dict(a)


def update_portal_article(
    db: Session, article_id, workspace_id, **kwargs,
) -> dict | None:
    a = db.query(PortalArticle).filter(
        PortalArticle.id == article_id,
        PortalArticle.workspace_id == workspace_id,
    ).first()
    if not a:
        return None
    if "title" in kwargs and kwargs["title"] is not None:
        a.title = kwargs["title"]
        a.slug = _slugify(kwargs["title"])
    if "content" in kwargs and kwargs["content"] is not None:
        a.content = kwargs["content"]
    if "category" in kwargs and kwargs["category"] is not None:
        a.category = kwargs["category"]
    if "product_area" in kwargs and kwargs["product_area"] is not None:
        a.product_area = kwargs["product_area"]
    if "tags" in kwargs and kwargs["tags"] is not None:
        a.tags_json = json.dumps(kwargs["tags"])
    if "published" in kwargs and kwargs["published"] is not None:
        a.published = kwargs["published"]
    db.flush()
    return _article_to_dict(a)


def delete_portal_article(db: Session, article_id, workspace_id) -> bool:
    a = db.query(PortalArticle).filter(
        PortalArticle.id == article_id,
        PortalArticle.workspace_id == workspace_id,
    ).first()
    if not a:
        return False
    db.delete(a)
    db.flush()
    return True


def mark_helpful(db: Session, article_id, workspace_id) -> bool:
    a = db.query(PortalArticle).filter(
        PortalArticle.id == article_id,
        PortalArticle.workspace_id == workspace_id,
    ).first()
    if not a:
        return False
    a.helpful_count += 1
    db.flush()
    return True


def search_portal_articles(
    db: Session, workspace_id, query: str,
) -> list[dict]:
    items = db.query(PortalArticle).filter(
        PortalArticle.workspace_id == workspace_id,
        PortalArticle.published.is_(True),
    ).all()
    lower = query.lower()
    matches = [
        a for a in items
        if lower in a.title.lower() or lower in a.content.lower()
        or any(lower in t.lower() for t in json.loads(a.tags_json))
    ]
    return [_article_to_dict(a) for a in matches[:20]]


def lookup_ticket_status(
    db: Session, ticket_id: str, workspace_id, email: str | None = None,
) -> dict | None:
    """Public endpoint: look up ticket status by ID."""
    try:
        tid = uuid.UUID(ticket_id)
    except ValueError:
        return None
    conv = db.query(Conversation).filter(
        Conversation.id == tid,
        Conversation.workspace_id == workspace_id,
    ).first()
    if not conv:
        return None

    if email:
        customer = db.query(CustomerProfile).filter(
            CustomerProfile.id == conv.customer_id,
            CustomerProfile.email == email,
        ).first()
        if not customer:
            return None

    return {
        "id": str(conv.id),
        "status": conv.status,
        "channel": conv.channel,
        "subject": conv.subject,
        "sentiment": conv.sentiment,
        "created_at": conv.created_at.isoformat() if conv.created_at else "",
        "last_message_at": conv.last_message_at.isoformat() if conv.last_message_at else "",
    }


def _article_to_dict(a: PortalArticle) -> dict:
    return {
        "id": str(a.id),
        "title": a.title,
        "slug": a.slug,
        "content": a.content,
        "category": a.category,
        "product_area": a.product_area,
        "tags": json.loads(a.tags_json) if a.tags_json else [],
        "published": a.published,
        "view_count": a.view_count,
        "helpful_count": a.helpful_count,
        "created_at": a.created_at.isoformat() if a.created_at else "",
        "updated_at": a.updated_at.isoformat() if a.updated_at else "",
    }
