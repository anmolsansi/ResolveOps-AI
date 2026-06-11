#!/usr/bin/env python3
"""Run V3 reliability smoke validation against a local ResolveOps AI API."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from v2_api_smoke import SmokeFailure, expect, get_json, post_json, run as run_v2


def run(base_url: str, csv_path: Path) -> None:
    run_v2(base_url, csv_path)

    cited = post_json(
        base_url,
        "/rag/query",
        {
            "question": "Customer reports duplicate invoice charge and needs refund guidance.",
            "top_k": 5,
        },
    )
    query_id = cited.get("query_id")
    expect(bool(query_id), "RAG query did not return query_id", cited)

    feedback = post_json(
        base_url,
        f"/rag/queries/{query_id}/feedback",
        {"feedback": "helpful"},
    )
    expect(feedback.get("feedback") == "helpful", "Feedback was not recorded", feedback)

    analytics = get_json(base_url, "/reliability/feedback")
    expect(analytics.get("total_feedback", 0) >= 1, "Feedback analytics missing feedback", analytics)
    expect(analytics.get("helpful_count", 0) >= 1, "Feedback analytics missing helpful count", analytics)

    fallback = post_json(
        base_url,
        "/rag/query",
        {"question": "Unrelated recipe question about desserts", "top_k": 3},
    )
    fallback_id = fallback.get("query_id")
    expect(bool(fallback_id), "Fallback query did not return query_id", fallback)

    review = post_json(
        base_url,
        f"/reliability/failed-queries/{fallback_id}/review",
        {"action": "ignored"},
    )
    expect(review.get("feedback") == "ignored", "Failed query review was not recorded", review)

    comparison = post_json(
        base_url,
        "/reliability/compare",
        {
            "name": "v3-smoke",
            "config_a": {"label": "Strict", "top_k": 3, "threshold": 0.6},
            "config_b": {"label": "Loose", "top_k": 5, "threshold": 0.3},
        },
    )
    expect(comparison.get("name") == "v3-smoke", "Comparison did not run", comparison)

    stored = get_json(base_url, "/reliability/comparisons")
    expect(bool(stored), "Stored comparisons missing", stored)
    expect(stored[0].get("name") == "compare:v3-smoke", "Stored comparison name mismatch", stored)

    print("V3 reliability smoke validation passed")


def main() -> int:
    parser = argparse.ArgumentParser(description="Run ResolveOps AI V3 reliability smoke validation")
    parser.add_argument("--base-url", default="http://localhost:8000")
    parser.add_argument("--csv", default="scripts/sample_tickets.csv")
    args = parser.parse_args()

    try:
        run(args.base_url.rstrip("/"), Path(args.csv))
    except SmokeFailure as exc:
        print(f"V3 reliability smoke validation failed: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
