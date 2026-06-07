"""Team knowledge-base generation from resolved tickets.

Groups resolved tickets that share a product area + issue type and distills a
KB article (summary, common resolution steps, source tickets). Regeneration is
idempotent: previously generated articles are replaced.
"""
import json
from collections import Counter, defaultdict

from sqlalchemy.orm import Session

from app.models.models import KbArticle, Ticket
from app.services.retrieval import _tokenize

RESOLVED_STATUSES = {"resolved", "closed", "done"}
MIN_CLUSTER_SIZE = 2
MAX_STEPS = 5
MAX_THEMES = 6


def _common_themes(tickets: list[Ticket]) -> list[str]:
    counter: Counter[str] = Counter()
    for t in tickets:
        counter.update(_tokenize(f"{t.title} {t.body}"))
    return [word for word, _ in counter.most_common(MAX_THEMES)]


def _resolution_steps(tickets: list[Ticket]) -> list[str]:
    steps: list[str] = []
    seen: set[str] = set()
    for t in sorted(tickets, key=lambda x: x.id):
        res = (t.resolution or "").strip()
        if res and res.lower() not in seen:
            seen.add(res.lower())
            steps.append(res)
        if len(steps) >= MAX_STEPS:
            break
    return steps


def generate_kb(db: Session, min_cluster_size: int = MIN_CLUSTER_SIZE) -> list[KbArticle]:
    resolved = [
        t
        for t in db.query(Ticket).all()
        if t.status.lower() in RESOLVED_STATUSES and (t.resolution or "").strip()
    ]

    groups: dict[tuple[str, str], list[Ticket]] = defaultdict(list)
    for t in resolved:
        groups[(t.product_area, t.issue_type)].append(t)

    db.query(KbArticle).delete()

    articles: list[KbArticle] = []
    for (area, issue_type), tickets in sorted(groups.items()):
        if len(tickets) < min_cluster_size:
            continue
        themes = _common_themes(tickets)
        steps = _resolution_steps(tickets)
        summary = (
            f"Synthesized from {len(tickets)} resolved {area} "
            f"{issue_type.lower()} tickets. Recurring themes: "
            f"{', '.join(themes) if themes else 'n/a'}."
        )
        article = KbArticle(
            title=f"{area} — {issue_type}: common resolutions",
            product_area=area,
            issue_type=issue_type,
            summary=summary,
            resolution_steps="\n".join(f"{i}. {s}" for i, s in enumerate(steps, 1)),
            source_ticket_ids_json=json.dumps(sorted(t.id for t in tickets)),
            ticket_count=len(tickets),
        )
        db.add(article)
        articles.append(article)

    db.commit()
    for a in articles:
        db.refresh(a)
    return articles
