#!/usr/bin/env python3
"""Run the V2 portfolio smoke path against a local ResolveOps AI API."""

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


def _read_json_response(req: request.Request, timeout: int = 20) -> dict:
    try:
        with request.urlopen(req, timeout=timeout) as response:
            body = response.read().decode("utf-8")
    except HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        raise SmokeFailure(f"HTTP {exc.code} for {req.full_url}: {detail}") from exc
    except URLError as exc:
        raise SmokeFailure(f"Could not reach {req.full_url}: {exc}") from exc

    try:
        return json.loads(body)
    except json.JSONDecodeError as exc:
        raise SmokeFailure(f"Expected JSON from {req.full_url}, got: {body[:300]}") from exc


def get_json(base_url: str, path: str) -> dict:
    return _read_json_response(request.Request(f"{base_url}{path}", method="GET"))


def post_json(base_url: str, path: str, payload: dict) -> dict:
    data = json.dumps(payload).encode("utf-8")
    req = request.Request(
        f"{base_url}{path}",
        data=data,
        method="POST",
        headers={"Content-Type": "application/json"},
    )
    return _read_json_response(req)


def upload_csv(base_url: str, csv_path: Path) -> dict:
    boundary = f"----ResolveOpsBoundary{uuid.uuid4().hex}"
    mime_type = mimetypes.guess_type(str(csv_path))[0] or "text/csv"
    file_bytes = csv_path.read_bytes()
    parts = [
        f"--{boundary}\r\n".encode("utf-8"),
        (
            'Content-Disposition: form-data; name="file"; '
            f'filename="{csv_path.name}"\r\n'
        ).encode("utf-8"),
        f"Content-Type: {mime_type}\r\n\r\n".encode("utf-8"),
        file_bytes,
        f"\r\n--{boundary}--\r\n".encode("utf-8"),
    ]
    body = b"".join(parts)
    req = request.Request(
        f"{base_url}/tickets/upload",
        data=body,
        method="POST",
        headers={
            "Content-Type": f"multipart/form-data; boundary={boundary}",
            "Content-Length": str(len(body)),
        },
    )
    return _read_json_response(req, timeout=60)


def expect(condition: bool, message: str, payload: object | None = None) -> None:
    if not condition:
        details = f"\nPayload: {payload}" if payload is not None else ""
        raise SmokeFailure(f"{message}{details}")


def run(base_url: str, csv_path: Path) -> None:
    health = get_json(base_url, "/health")
    expect(health.get("status") == "ok", "Health check failed", health)

    upload = upload_csv(base_url, csv_path)
    expect(upload.get("valid_count", 0) > 0, "CSV upload did not store valid tickets", upload)
    expect(
        upload.get("embedding_failure_count", 0) == 0,
        "CSV upload had embedding failures in mock mode",
        upload,
    )

    cited = post_json(
        base_url,
        "/rag/query",
        {
            "question": (
                "Customer has a duplicate invoice charge and needs a billing refund. "
                "What fixed this before?"
            ),
            "top_k": 5,
        },
    )
    expect(bool(cited.get("citations")), "Expected cited RAG answer", cited)
    expect(cited.get("confidence", 0) >= 0.3, "Expected confident RAG answer", cited)
    retrieved = cited.get("retrieved_chunks") or []
    expect(bool(retrieved), "Expected retrieved chunks", cited)
    expect(
        any(chunk.get("debug") for chunk in retrieved),
        "Expected retrieval debug details",
        cited,
    )

    fallback = post_json(
        base_url,
        "/rag/query",
        {
            "question": "Give me a chocolate cake frosting recipe with bananas and cinnamon.",
            "top_k": 3,
        },
    )
    expect(not fallback.get("citations"), "Fallback query should not cite tickets", fallback)
    expect(fallback.get("is_fallback") is True, "Fallback query should set is_fallback", fallback)
    expect(
        "enough context" in str(fallback.get("answer", "")).lower(),
        "Fallback answer should explain insufficient context",
        fallback,
    )

    eval_run = post_json(base_url, "/eval/run", {"name": "v2-smoke"})
    run_id = eval_run.get("id")
    expect(bool(run_id), "Eval run did not return an id", eval_run)
    expect(eval_run.get("total_questions", 0) > 0, "Eval run had no questions", eval_run)

    export = get_json(base_url, f"/eval/runs/{run_id}/export?format=json")
    expect(export.get("id") == run_id, "Eval export did not match run id", export)

    quality = get_json(base_url, "/dashboard/quality")
    expect(quality.get("total_valid_rows", 0) > 0, "Quality dashboard missing valid rows", quality)

    retrieval = get_json(base_url, "/dashboard/retrieval")
    expect(retrieval.get("total_queries", 0) >= 2, "Retrieval dashboard missing queries", retrieval)

    charts = get_json(base_url, "/dashboard/charts")
    expect(bool(charts.get("ingestion")), "Chart data missing ingestion points", charts)
    expect(bool(charts.get("queries")), "Chart data missing query points", charts)

    print("V2 smoke validation passed")


def main() -> int:
    parser = argparse.ArgumentParser(description="Run ResolveOps AI V2 smoke validation")
    parser.add_argument("--base-url", default="http://localhost:8000")
    parser.add_argument("--csv", default="scripts/sample_tickets.csv")
    args = parser.parse_args()

    try:
        run(args.base_url.rstrip("/"), Path(args.csv))
    except SmokeFailure as exc:
        print(f"V2 smoke validation failed: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
