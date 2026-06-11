#!/usr/bin/env python3
"""Wait for the local API health endpoint."""

from __future__ import annotations

import json
import sys
import time
from urllib import request
from urllib.error import URLError

URL = "http://localhost:8000/health"


def main() -> int:
    for attempt in range(1, 31):
        try:
            with request.urlopen(URL, timeout=3) as response:
                payload = json.loads(response.read().decode("utf-8"))
            if payload.get("status") == "ok":
                print("Backend is ready")
                return 0
        except (URLError, TimeoutError, json.JSONDecodeError):
            pass
        print(f"Waiting for backend... ({attempt}/30)")
        time.sleep(2)
    print("Backend failed to become ready", file=sys.stderr)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
