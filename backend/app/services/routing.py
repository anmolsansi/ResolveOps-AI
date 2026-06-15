"""V9 routing service: matches incoming conversations against rules and
applies auto-assignment and priority actions."""
import json
import uuid

from sqlalchemy.orm import Session

from app.models.models import Conversation, RoutingRule


def list_routing_rules(db: Session, workspace_id) -> list[dict]:
    rules = (
        db.query(RoutingRule)
        .filter(RoutingRule.workspace_id == workspace_id)
        .order_by(RoutingRule.priority.desc())
        .all()
    )
    return [_rule_to_dict(r) for r in rules]


def get_routing_rule(db: Session, rule_id, workspace_id) -> dict | None:
    rule = db.query(RoutingRule).filter(
        RoutingRule.id == rule_id,
        RoutingRule.workspace_id == workspace_id,
    ).first()
    return _rule_to_dict(rule) if rule else None


def create_routing_rule(
    db: Session, workspace_id, name: str, description: str | None,
    priority: int, conditions: dict, actions: dict,
) -> dict:
    rule = RoutingRule(
        id=uuid.uuid4(),
        workspace_id=workspace_id,
        name=name,
        description=description,
        priority=priority,
        conditions_json=json.dumps(conditions),
        actions_json=json.dumps(actions),
    )
    db.add(rule)
    db.flush()
    return _rule_to_dict(rule)


def update_routing_rule(
    db: Session, rule_id, workspace_id, **kwargs,
) -> dict | None:
    rule = db.query(RoutingRule).filter(
        RoutingRule.id == rule_id,
        RoutingRule.workspace_id == workspace_id,
    ).first()
    if not rule:
        return None
    if "name" in kwargs and kwargs["name"] is not None:
        rule.name = kwargs["name"]
    if "description" in kwargs and kwargs["description"] is not None:
        rule.description = kwargs["description"]
    if "priority" in kwargs and kwargs["priority"] is not None:
        rule.priority = kwargs["priority"]
    if "enabled" in kwargs and kwargs["enabled"] is not None:
        rule.enabled = kwargs["enabled"]
    if "conditions" in kwargs and kwargs["conditions"] is not None:
        rule.conditions_json = json.dumps(kwargs["conditions"])
    if "actions" in kwargs and kwargs["actions"] is not None:
        rule.actions_json = json.dumps(kwargs["actions"])
    db.flush()
    return _rule_to_dict(rule)


def delete_routing_rule(db: Session, rule_id, workspace_id) -> bool:
    rule = db.query(RoutingRule).filter(
        RoutingRule.id == rule_id,
        RoutingRule.workspace_id == workspace_id,
    ).first()
    if not rule:
        return False
    db.delete(rule)
    db.flush()
    return True


def match_rules(db: Session, workspace_id, conversation: Conversation) -> list[dict]:
    """Find all matching rules for a conversation, ordered by priority."""
    rules = (
        db.query(RoutingRule)
        .filter(
            RoutingRule.workspace_id == workspace_id,
            RoutingRule.enabled.is_(True),
        )
        .order_by(RoutingRule.priority.desc())
        .all()
    )
    matched = []
    for rule in rules:
        conditions = json.loads(rule.conditions_json)
        if _conditions_match(conditions, conversation):
            rule.match_count += 1
            matched.append(_rule_to_dict(rule))
    if matched:
        db.flush()
    return matched


def apply_actions(
    db: Session, conversation: Conversation, actions: dict,
) -> None:
    """Apply routing actions to a conversation."""
    if "set_priority" in actions:
        # Store in metadata — conversation model doesn't have priority
        pass
    if "set_product_area" in actions:
        conversation.product_area = actions["set_product_area"]
    if "set_status" in actions:
        conversation.status = actions["set_status"]
    db.flush()


def _conditions_match(conditions: dict, conv: Conversation) -> bool:
    if not conditions:
        return False
    if "product_area" in conditions:
        if conv.product_area != conditions["product_area"]:
            return False
    if "sentiment" in conditions:
        if conv.sentiment != conditions["sentiment"]:
            return False
    if "channel" in conditions:
        if conv.channel != conditions["channel"]:
            return False
    if "status" in conditions:
        if conv.status != conditions["status"]:
            return False
    return True


def _rule_to_dict(rule: RoutingRule) -> dict:
    return {
        "id": str(rule.id),
        "name": rule.name,
        "description": rule.description,
        "priority": rule.priority,
        "enabled": rule.enabled,
        "conditions": json.loads(rule.conditions_json),
        "actions": json.loads(rule.actions_json),
        "match_count": rule.match_count,
        "created_at": rule.created_at.isoformat() if rule.created_at else "",
    }
