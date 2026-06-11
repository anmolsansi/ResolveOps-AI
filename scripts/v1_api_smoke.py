#!/usr/bin/env python3
"""Run the ResolveOps AI V1 smoke path against a local Docker startup.

V1 validates only the original MVP contract:
- backend health
- frontend is reachable
- CSV upload stores valid tickets and invalid row details
- ticket list/detail APIs work
- cited RAG answer works
- low-confidence fallback works
- dashboard quality/retrieval metrics update from real database rows
- eval run is created and listed

This script intentionally uses only the Python standard library so it can run in
GitHub Actions without extra dependencies.
"""

from __future__ import annotations

import argparse
import json
import mimetypes
import sys
import uuid
from pathlib import Path
from urllib import request
from urllib.error import HTTPError, URLError


class SmokeFailure(RuntimeError):
    pass


def _read_response(req: request.Request, timeout: int = 30) -> tuple[int, str]:
    try:
        with request.urlopen(req, timeout=timeout) as response:
            return response.status, response.read().decode("utf-8", errors="replace")
    except HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        raise SmokeFailure(f"HTTP {exc.code} for {req.full_url}: {detail}") from exc
    except URLError as exc:
        raise SmokeFailure(f"Could not reach {req.full_url}: {exc}") from exc


def _json(req: request.Request, timeout: int = 30) -> dict:
    _, body = _read_response(req, timeout=timeout)
    try:
        parsed = json.loads(body)
    except json.JSONDecodeError as exc:
        raise SmokeFailure(f"Expected JSON from {req.full_url}, got: {body[:300]}") from exc
    if not isinstance(parsed, dict):
        raise SmokeFailure(f"Expected JSON object from {req.full_url}, got: {type(parsed).__name__}")
    return parsed


def get_json(base_url: str, path: str) -> dict:
    return _json(request.Request(f"{base_url}{path}", method="GET"))


def post_json(base_url: str, path: str, payload: dict) -> dict:
    data = json.dumps(payload).encode("utf-8")
    req = request.Request(
        f"{base_url}{path}",
        data=data,
        method="POST",
        headers={"Content-Type": "application/json"},
    )
    return _json(req)


def upload_csv(base_url: str, csv_path: Path) -> dict:
    if not csv_path.exists():
        raise SmokeFailure(f"CSV file does not exist: {csv_path}")

    boundary = f"----ResolveOpsBoundary{uuid.uuid4().hex}"
    mime_type = mimetypes.guess_type(str(csv_path))[0] or "text/csv"
    file_bytes = csv_path.read_bytes()
    body = b"".join(
        [
            f"--{boundary}\r\n".encode("utf-8"),
            (
                'Content-Disposition: form-data; name="file"; '
                f'filename="{csv_path.name}"\r\n'
            ).encode("utf-8"),
            f"Content-Type: {mime_type}\r\n\r\n".encode("utf-8"),
            file_bytes,
            f"\r\n--{boundary}--\r\n".encode("utf-8"),
        ]
    )
    req = request.Request(
        f"{base_url}/tickets/upload",
        data=body,
        method="POST",
        headers={
            "Content-Type": f"multipart/form-data; boundary={boundary}",
            "Content-Length": str(len(body)),
        },
    )
    return _json(req, timeout=90)


def expect(condition: bool, message: str, payload: object | None = None) -> None:
    if not condition:
        details = f"\nPayload: {payload}" if payload is not None else ""
        raise SmokeFailure(f"{message}{details}")


def check_frontend(frontend_url: str) -> None:
    req = request.Request(frontend_url, method="GET")
    status, body = _read_response(req, timeout=20)
    expect(status == 200, "Frontend did not return HTTP 200", {"status": status})
    expect(
        "root" in body or "ResolveOps" in body or "script" in body,
        "Frontend response did not look like the React app shell",
        body[:300],
    )


def run(base_url: str, csv_path: Path, frontend_url: str | None = None) -> None:
    health = get_json(base_url, "/health")
    expect(health.get("status") == "ok", "Backend health check failed", health)

    if frontend_url:
        check_frontend(frontend_url)

    upload = upload_csv(base_url, csv_path)
    expect(upload.get("total_count", 0) > 0, "CSV upload did not see rows", upload)
    expect(upload.get("valid_count", 0) > 0, "CSV upload did not store valid tickets", upload)
    expect(upload.get("embedding_failure_count", 0) == 0, "Embedding failures in mock mode", upload)
    expect("invalid_rows" in upload, "Upload response missing invalid_rows field", upload)

    tickets = get_json(base_url, "/tickets?page=1&page_size=5")
    expect(tickets.get("total", 0) > 0, "Ticket list is empty after upload", tickets)
    first_ticket = tickets["items"][0]
    ticket_detail = get_json(base_url, f"/tickets/{first_ticket['id']}")
    expect(ticket_detail.get("id") == first_ticket["id"], "Ticket detail did not match list item", ticket_detail)
    expect(bool(ticket_detail.get("chunks")), "Ticket detail missing chunk previews", ticket_detail)

    cited = post_json(
        base_url,
        "/rag/query",
        {
            "question": "Customer has a duplicate invoice charge and needs refund guidance. What fixed this before?",
            "top_k": 5,
        },
    )
    expect(bool(cited.get("query_id")), "RAG query did not return query_id", cited)
    expect(bool(cited.get("citations")), "Expected cited RAG answer", cited)
    expect(cited.get("confidence", 0) >= 0.3, "Expected confident RAG answer", cited)
    expect(cited.get("latency_ms", -1) >= 0, "RAG response missing latency", cited)
    expect("quality" in cited, "RAG response missing quality scores", cited)

    fallback = post_json(
        base_url,
        "/rag/query",
        {"question": "Explain how to bake a chocolate cake with bananas", "top_k": 3},
    )
    expect(not fallback.get("citations"), "Fallback query should not cite tickets", fallback)
    expect(fallback.get("is_fallback") is True, "Fallback query should set is_fallback", fallback)
    expect("enough context" in str(fallback.get("answer", "")).lower(), "Fallback answer should explain insufficient context", fallback)

    quality = get_json(base_url, "/dashboard/quality")
    expect(quality.get("total_valid_rows", 0) > 0, "Quality dashboard missing valid rows", quality)
    expect(quality.get("total_batches", 0) > 0, "Quality dashboard missing ingestion batch", quality)

    retrieval = get_json(base_url, "/dashboard/retrieval")
    expect(retrieval.get("total_queries", 0) >= 2, "Retrieval dashboard missing RAG queries", retrieval)
    expect(retrieval.get("citation_rate", 0) > 0, "Retrieval dashboard missing citation rate", retrieval)

    eval_run = post_json(base_url, "/eval/run", {"name": "v1-smoke"})
    expect(bool(eval_run.get("id")), "Eval run did not return id", eval_run)
    expect(eval_run.get("total_questions", 0) > 0, "Eval run had no questions", eval_run)

    eval_runs = _read_response(request.Request(f"{base_url}/eval/runs", method="GET"))[1]
    try:
        parsed_runs = json.loads(eval_runs)
    except json.JSONDecodeError as exc:
        raise SmokeFailure(f"Eval runs response was not JSON: {eval_runs[:300]}") from exc
    expect(isinstance(parsed_runs, list) and parsed_runs, "Eval runs list is empty", parsed_runs)

    print("V1 smoke validation passed")


def main() -> int:
    parser = argparse.ArgumentParser(description="Run ResolveOps AI V1 smoke validation")
    parser.add_argument("--base-url", default="http://localhost:8000")
    parser.add_argument("--frontend-url", default="http://localhost:5173")
    parser.add_argument("--csv", default="scripts/sample_tickets.csv")
    args = parser.parse_args()

    try:
        run(args.base_url.rstrip("/"), Path(args.csv), args.frontend_url.rstrip("/"))
    except SmokeFailure as exc:
        print(f"V1 smoke validation failed: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
