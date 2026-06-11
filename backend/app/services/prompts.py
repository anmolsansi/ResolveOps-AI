"""Prompt template version management.

Each ``name`` is a prompt family; creating a prompt with an existing name adds
a new incrementing version. Exactly one template can be active at a time and is
consumed by answer generation (see ``providers``).
"""
from __future__ import annotations

from sqlalchemy.orm import Session

from app.models.models import PromptTemplate

DEFAULT_PROMPT = (
    "You are a customer-support assistant. Answer using only the provided "
    "ticket context and cite the ticket IDs you used. If the context is "
    "insufficient, say so instead of guessing."
)


def next_version(db: Session, name: str) -> int:
    latest = (
        db.query(PromptTemplate)
        .filter(PromptTemplate.name == name)
        .order_by(PromptTemplate.version.desc())
        .first()
    )
    return (latest.version + 1) if latest else 1


def create_prompt(db: Session, name: str, content: str, activate: bool = False) -> PromptTemplate:
    prompt = PromptTemplate(
        name=name,
        version=next_version(db, name),
        content=content,
        is_active=False,
    )
    db.add(prompt)
    db.flush()
    if activate:
        _set_active(db, prompt)
    db.commit()
    db.refresh(prompt)
    return prompt


def _set_active(db: Session, prompt: PromptTemplate) -> None:
    db.query(PromptTemplate).filter(PromptTemplate.is_active.is_(True)).update(
        {"is_active": False}, synchronize_session=False
    )
    prompt.is_active = True


def activate_prompt(db: Session, prompt: PromptTemplate) -> PromptTemplate:
    _set_active(db, prompt)
    db.commit()
    db.refresh(prompt)
    return prompt


def get_active_prompt(db: Session) -> PromptTemplate | None:
    return db.query(PromptTemplate).filter(PromptTemplate.is_active.is_(True)).first()


def get_active_prompt_text(db: Session) -> str:
    active = get_active_prompt(db)
    return active.content if active else DEFAULT_PROMPT
