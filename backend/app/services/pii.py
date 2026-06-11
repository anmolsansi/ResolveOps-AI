"""PII detection and redaction using deterministic regex patterns.

Detects emails, phone numbers, US SSNs, credit-card numbers, and IPv4
addresses. Redaction replaces each match with a typed placeholder, e.g.
``[REDACTED_EMAIL]``. Pure-function and deterministic so it is fully testable
in mock mode.
"""
from __future__ import annotations

import re

# Order matters: more specific patterns first so they win overlap resolution.
_PATTERNS: list[tuple[str, re.Pattern[str]]] = [
    ("email", re.compile(r"[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}")),
    ("ssn", re.compile(r"\b\d{3}-\d{2}-\d{4}\b")),
    ("credit_card", re.compile(r"\b(?:\d[ -]*?){13,16}\b")),
    (
        "phone",
        re.compile(
            r"(?<!\d)(?:\+?\d{1,2}[\s.\-]?)?(?:\(\d{3}\)|\d{3})[\s.\-]\d{3}[\s.\-]\d{4}(?!\d)"
        ),
    ),
    ("ip_address", re.compile(r"\b(?:\d{1,3}\.){3}\d{1,3}\b")),
]


def detect_pii(text: str) -> list[dict]:
    """Return non-overlapping matches as dicts: type, value, start, end."""
    matches: list[dict] = []
    claimed: list[tuple[int, int]] = []

    def _overlaps(start: int, end: int) -> bool:
        return any(start < c_end and end > c_start for c_start, c_end in claimed)

    for pii_type, pattern in _PATTERNS:
        for m in pattern.finditer(text):
            start, end = m.start(), m.end()
            value = m.group()
            # credit-card pattern is greedy on digit runs; require >= 13 digits
            if pii_type == "credit_card" and len(re.sub(r"\D", "", value)) < 13:
                continue
            if _overlaps(start, end):
                continue
            claimed.append((start, end))
            matches.append({"type": pii_type, "value": value, "start": start, "end": end})

    matches.sort(key=lambda x: x["start"])
    return matches


def redact_pii(text: str) -> tuple[str, dict[str, int]]:
    """Return (redacted_text, counts_by_type)."""
    matches = detect_pii(text)
    counts: dict[str, int] = {}
    # Replace from the end so earlier indices stay valid.
    redacted = text
    for m in sorted(matches, key=lambda x: x["start"], reverse=True):
        placeholder = f"[REDACTED_{m['type'].upper()}]"
        redacted = redacted[: m["start"]] + placeholder + redacted[m["end"] :]
        counts[m["type"]] = counts.get(m["type"], 0) + 1
    return redacted, counts
