"""Answer-quality and reliability scoring.

All scores are deterministic heuristics in [0, 1] so they work in mock mode and
in tests without calling a real model. They are intentionally simple and
explainable — the goal is observability, not a perfect judge.

Definitions (let q = query tokens, a = answer tokens, c_i = tokens of retrieved
chunk i, all_ctx = union of c_i, cited_ctx = union of c_i for cited tickets):

- retrieval_precision = (# retrieved chunks sharing a token with q) / (# chunks)
- citation_coverage   = |a ∩ cited_ctx| / |a|   (answer backed by cited sources)
- hallucination_risk  = |a − all_ctx| / |a|     (answer content with no support)
- answer_completeness = |q ∩ a| / |q|           (question terms addressed)

Fallback answers make no factual claim, so their coverage / risk / completeness
are reported as 0.
"""

from app.services.retrieval import _tokenize


def _safe_ratio(num: int, denom: int) -> float:
    return round(num / denom, 4) if denom > 0 else 0.0


def compute_quality_metrics(
    question: str,
    answer: str,
    retrieved: list[dict],
    citations: list[str],
    is_fallback: bool,
) -> dict[str, float]:
    q_tokens = _tokenize(question)

    relevant = 0
    all_ctx: set[str] = set()
    cited_ctx: set[str] = set()
    cited_set = set(citations)
    for chunk in retrieved:
        c_tokens = _tokenize(chunk.get("text", ""))
        all_ctx |= c_tokens
        if q_tokens & c_tokens:
            relevant += 1
        if chunk.get("ticket_id") in cited_set:
            cited_ctx |= c_tokens

    retrieval_precision = _safe_ratio(relevant, len(retrieved))

    if is_fallback:
        return {
            "retrieval_precision": retrieval_precision,
            "citation_coverage": 0.0,
            "hallucination_risk": 0.0,
            "answer_completeness": 0.0,
        }

    a_tokens = _tokenize(answer)
    citation_coverage = _safe_ratio(len(a_tokens & cited_ctx), len(a_tokens))
    hallucination_risk = _safe_ratio(len(a_tokens - all_ctx), len(a_tokens))
    answer_completeness = _safe_ratio(len(q_tokens & a_tokens), len(q_tokens))

    return {
        "retrieval_precision": retrieval_precision,
        "citation_coverage": citation_coverage,
        "hallucination_risk": hallucination_risk,
        "answer_completeness": answer_completeness,
    }


def percentile(values: list[float], pct: float) -> float:
    """Nearest-rank percentile. pct in [0, 100]."""
    if not values:
        return 0.0
    ordered = sorted(values)
    if len(ordered) == 1:
        return round(ordered[0], 2)
    rank = (pct / 100) * (len(ordered) - 1)
    lower = int(rank)
    upper = min(lower + 1, len(ordered) - 1)
    frac = rank - lower
    interpolated = ordered[lower] + (ordered[upper] - ordered[lower]) * frac
    return round(interpolated, 2)
