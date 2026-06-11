#!/usr/bin/env python3
"""Wait for the local API health endpoint."""

from __future__ import annotations

import http.client
import json
import os
import socket
import sys
import time
from urllib import request
from urllib.error import HTTPError, URLError

URL = os.environ.get("API_HEALTH_URL", "http://localhost:8000/health")
ATTEMPTS = int(os.environ.get("API_WAIT_ATTEMPTS", "60"))
SLEEP_SECONDS = float(os.environ.get("API_WAIT_SLEEP_SECONDS", "2"))
TIMEOUT_SECONDS = float(os.environ.get("API_WAIT_TIMEOUT_SECONDS", "3"))


RETRYABLE_ERRORS = (
    HTTPError,
    URLError,
    TimeoutError,
    ConnectionError,
    ConnectionResetError,
    BrokenPipeError,
    socket.timeout,
    http.client.HTTPException,
    OSError,
    json.JSONDecodeError,
)


def main() -> int:
    last_error = "backend did not return ready status"

    for attempt in range(1, ATTEMPTS + 1):
        try:
            with request.urlopen(URL, timeout=TIMEOUT_SECONDS) as response:
                payload = json.loads(response.read().decode("utf-8"))
            if payload.get("status") == "ok":
                print("Backend is ready")
                return 0
            last_error = f"unexpected health payload: {payload}"
        except RETRYABLE_ERRORS as exc:
            last_error = f"{type(exc).__name__}: {exc}"

        print(f"Waiting for backend... ({attempt}/{ATTEMPTS}) - {last_error}")
        if attempt < ATTEMPTS:
            time.sleep(SLEEP_SECONDS)

    print(f"Backend failed to become ready: {last_error}", file=sys.stderr)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
