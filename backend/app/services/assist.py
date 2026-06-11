"""Live-ticket assistance: suggested drafts, escalation, and tier-aware guidance.

Reuses the RAG retrieval pipeline to ground suggestions in resolved tickets and
produces two modes: a customer-facing draft and an internal agent note.
"""
from app.core.config import settings
from app.services.prompts import get_active_prompt_text
from app.services.providers.factory import get_answer_provider
from app.services.retrieval import compute_confidence, retrieve_chunks

ANSWER_THRESHOLD = 0.6

TIER_GUIDANCE = {
    "enterprise": (
        "Enterprise customer — apply priority SLA, proactively offer a call, "
        "and notify the account manager."
    ),
    "pro": "Pro customer — respond within standard SLA and confirm the fix resolved it.",
    "free": (
        "Free tier — lead with self-serve docs; escalate only for confirmed "
        "outages or billing errors."
    ),
}

_HOLDING_MESSAGE = (
    "Thanks for reaching out. We're looking into this now and a support "
    "specialist will follow up shortly with details specific to your account."
)


def build_assist(
    db,
    subject: str,
    body: str,
    customer_tier: str | None = None,
    product_area: str | None = None,
    top_k: int = 5,
) -> dict:
    question = f"{subject}\n{body}".strip()
    filters: dict[str, str | None] | None = (
        {"product_area": product_area} if product_area else None
    )
    results = retrieve_chunks(db, question, filters=filters, top_k=top_k)
    confidence = compute_confidence([r["score"] for r in results])
    retrieved_ticket_ids = list(dict.fromkeys(r["ticket_id"] for r in results))

    clarify_threshold = settings.low_confidence_threshold
    if results and confidence >= ANSWER_THRESHOLD:
        recommendation = "answer"
        rec_reason = "Strong match to resolved tickets — a confident answer can be sent."
    elif results and confidence >= clarify_threshold:
        recommendation = "ask_clarification"
        rec_reason = "Partial match — confirm details with the customer before committing."
    else:
        recommendation = "route_to_human"
        rec_reason = "No strong knowledge-base match — route to a human agent."

    provider = get_answer_provider()
    system_prompt = get_active_prompt_text(db)
    if recommendation == "answer":
        contexts = [{"ticket_id": r["ticket_id"], "text": r["text"]} for r in results]
        customer_facing = provider.generate_answer(question, contexts, system_prompt=system_prompt)
        customer_citations = retrieved_ticket_ids
    elif recommendation == "ask_clarification":
        contexts = [{"ticket_id": r["ticket_id"], "text": r["text"]} for r in results]
        draft = provider.generate_answer(question, contexts, system_prompt=system_prompt)
        customer_facing = (
            "To make sure I point you to the right fix, could you confirm the "
            "affected account, when the issue started, and any exact error "
            f"message? In the meantime, this often helps: {draft}"
        )
        customer_citations = retrieved_ticket_ids
    else:
        customer_facing = _HOLDING_MESSAGE
        customer_citations = []

    tier_note = TIER_GUIDANCE.get(
        (customer_tier or "").lower(), "Standard handling — follow the default SLA."
    )

    internal_note = (
        f"Recommendation: {recommendation} — {rec_reason}\n"
        f"Confidence: {confidence:.2f}\n"
        f"Closest tickets: {', '.join(retrieved_ticket_ids) or 'none'}\n"
        f"Tier guidance: {tier_note}"
    )

    return {
        "recommendation": recommendation,
        "recommendation_reason": rec_reason,
        "confidence": confidence,
        "customer_facing_draft": customer_facing,
        "internal_note": internal_note,
        "citations": customer_citations,
        "tier_guidance": tier_note,
        "retrieved": [
            {
                "ticket_id": r["ticket_id"],
                "score": r["score"],
                "preview": r["preview"],
                "product_area": r.get("product_area"),
            }
            for r in results
        ],
    }
