#!/usr/bin/env python3
"""Run V4 workflow integration smoke validation against a local ResolveOps AI API."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from v2_api_smoke import SmokeFailure, expect, get_json, post_json, run as run_v2


def run(base_url: str, csv_path: Path) -> None:
    run_v2(base_url, csv_path)

    # Create Zendesk connector
    zd = post_json(base_url, "/connectors", {"provider": "zendesk", "name": "Smoke ZD"})
    expect(zd.get("id"), "Zendesk connector not created", zd)
    zd_id = zd["id"]

    # Sync Zendesk (imports tickets + dedup)
    sync = post_json(base_url, f"/connectors/{zd_id}/sync?limit=10")
    expect(sync.get("imported", 0) == 6, "Expected 6 imported tickets", sync)
    expect(sync.get("duplicate_semantic", 0) == 1, "Expected 1 semantic duplicate", sync)

    # Incremental sync
    sync2 = post_json(base_url, f"/connectors/{zd_id}/sync?limit=10")
    expect(sync2.get("fetched", 0) == 0, "Incremental sync should fetch 0", sync2)

    # Create Freshdesk connector
    fd = post_json(base_url, "/connectors", {"provider": "freshdesk", "name": "Smoke FD"})
    fd_id = fd["id"]

    # Sync Freshdesk
    fd_sync = post_json(base_url, f"/connectors/{fd_id}/sync?limit=10")
    expect(fd_sync.get("imported", 0) == 6, "Expected 6 imported from Freshdesk", fd_sync)

    # Create scheduled job
    job = post_json(base_url, f"/connectors/{fd_id}/jobs", {"interval_minutes": 60})
    expect(job.get("interval_minutes") == 60, "Job interval not set", job)

    # Run due jobs
    run_due = post_json(base_url, "/connectors/jobs/run-due?limit=10")
    expect(run_due.get("ran", 0) >= 1, "No jobs ran", run_due)

    # Check duplicates endpoint
    dupes = get_json(base_url, "/connectors/duplicates")
    expect(isinstance(dupes.get("clusters"), list), "Duplicates endpoint failed", dupes)

    # Assist draft - related query
    assist = post_json(
        base_url,
        "/assist/draft",
        {
            "subject": "Login fails after password reset",
            "body": "I reset my password and now cannot log in",
            "customer_tier": "Enterprise",
        },
    )
    expect(assist.get("recommendation") in {"answer", "ask_clarification"}, "Assist should recommend answer/clarification", assist)
    expect(len(assist.get("citations", [])) > 0, "Assist should have citations", assist)

    # Assist draft - unrelated query
    assist2 = post_json(
        base_url,
        "/assist/draft",
        {"subject": "Best pizza recipe", "body": "How much cheese?"},
    )
    expect(assist2.get("recommendation") == "route_to_human", "Assist should route to human", assist2)

    # KB generation
    kb = post_json(base_url, "/kb/generate")
    expect(kb.get("generated", 0) >= 1, "KB should generate at least 1 article", kb)
    expect(len(kb.get("items", [])) >= 1, "KB items missing", kb)

    # SLA risk
    sla = get_json(base_url, "/sla/risks")
    expect("items" in sla, "SLA risks missing items", sla)

    print("V4 workflow smoke validation passed")


def main() -> int:
    parser = argparse.ArgumentParser(description="Run ResolveOps AI V4 workflow smoke validation")
    parser.add_argument("--base-url", default="http://localhost:8000")
    parser.add_argument("--csv", default="scripts/sample_tickets.csv")
    args = parser.parse_args()

    try:
        run(args.base_url.rstrip("/"), Path(args.csv))
    except SmokeFailure as exc:
        print(f"V4 workflow smoke validation failed: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())