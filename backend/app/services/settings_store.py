"""Runtime application settings backed by the ``app_settings`` table.

Effective config = environment defaults (``settings``) overlaid with any values
an admin has persisted at runtime. Mock mode short-circuits provider selection
elsewhere, so overriding ``llm_provider`` here never breaks tests.
"""
from __future__ import annotations

from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.models import AppSetting

# key -> (type, env-default-attribute or literal default)
_DEFAULTS: dict[str, tuple[str, object]] = {
    "llm_provider": ("str", settings.llm_provider),
    "embedding_provider": ("str", settings.embedding_provider),
    "llm_model": ("str", "gpt-4o-mini"),
    "embedding_model": ("str", "text-embedding-3-small"),
    "low_confidence_threshold": ("float", settings.low_confidence_threshold),
    "default_top_k": ("int", settings.default_top_k),
    "vector_backend": ("str", settings.vector_backend),
    "pii_redaction_enabled": ("bool", settings.pii_redaction_enabled),
    "retention_rag_query_days": ("int", settings.retention_rag_query_days),
    "retention_audit_log_days": ("int", settings.retention_audit_log_days),
    "active_prompt_id": ("str", ""),
}


def _coerce(kind: str, raw: str) -> object:
    if kind == "int":
        return int(raw)
    if kind == "float":
        return float(raw)
    if kind == "bool":
        return raw.lower() in {"1", "true", "yes", "on"}
    return raw


def get_setting(db: Session, key: str) -> object:
    kind, default = _DEFAULTS[key]
    row = db.get(AppSetting, key)
    if row is None:
        return default
    return _coerce(kind, row.value)


def get_int_setting(db: Session, key: str) -> int:
    value = get_setting(db, key)
    return int(value) if isinstance(value, (int, float, str)) else 0


def get_bool_setting(db: Session, key: str) -> bool:
    return bool(get_setting(db, key))


def get_str_setting(db: Session, key: str) -> str:
    return str(get_setting(db, key))


def get_all_settings(db: Session) -> dict[str, object]:
    return {key: get_setting(db, key) for key in _DEFAULTS}


def set_setting(db: Session, key: str, value: object, *, commit: bool = True) -> None:
    if key not in _DEFAULTS:
        raise KeyError(key)
    row = db.get(AppSetting, key)
    serialized = str(value)
    if row is None:
        db.add(AppSetting(key=key, value=serialized))
    else:
        row.value = serialized
    if commit:
        db.commit()


def apply_updates(db: Session, updates: dict[str, object]) -> list[str]:
    changed: list[str] = []
    for key, value in updates.items():
        if value is None or key not in _DEFAULTS:
            continue
        set_setting(db, key, value, commit=False)
        changed.append(key)
    db.commit()
    return changed
