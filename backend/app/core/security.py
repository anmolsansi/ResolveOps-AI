"""Security primitives: password hashing and signed access tokens.

Uses only the Python standard library (no bcrypt/PyJWT dependency) so the
project stays dependency-light and runs in mock mode without extra installs.

- Passwords: PBKDF2-HMAC-SHA256 with a per-password random salt.
- Tokens: compact JWT-like tokens (header.payload.signature) signed with
  HMAC-SHA256 using ``settings.secret_key``.
"""
from __future__ import annotations

import base64
import hashlib
import hmac
import json
import secrets
import time

from app.core.config import settings

_PBKDF2_ROUNDS = 120_000
_ALGO = "pbkdf2_sha256"


def hash_password(password: str) -> str:
    salt = secrets.token_hex(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode(), salt.encode(), _PBKDF2_ROUNDS)
    return f"{_ALGO}${_PBKDF2_ROUNDS}${salt}${digest.hex()}"


def verify_password(password: str, stored: str) -> bool:
    try:
        algo, rounds_s, salt, expected = stored.split("$")
    except ValueError:
        return False
    if algo != _ALGO:
        return False
    digest = hashlib.pbkdf2_hmac("sha256", password.encode(), salt.encode(), int(rounds_s))
    return hmac.compare_digest(digest.hex(), expected)


def _b64encode(raw: bytes) -> str:
    return base64.urlsafe_b64encode(raw).rstrip(b"=").decode()


def _b64decode(data: str) -> bytes:
    padding = "=" * (-len(data) % 4)
    return base64.urlsafe_b64decode(data + padding)


def _sign(message: bytes) -> str:
    sig = hmac.new(settings.secret_key.encode(), message, hashlib.sha256).digest()
    return _b64encode(sig)


def create_access_token(
    subject: str, email: str, role: str, expires_minutes: int | None = None
) -> str:
    expires = (
        expires_minutes
        if expires_minutes is not None
        else settings.access_token_expire_minutes
    )
    header = {"alg": "HS256", "typ": "JWT"}
    payload = {
        "sub": subject,
        "email": email,
        "role": role,
        "exp": int(time.time()) + expires * 60,
        "iat": int(time.time()),
    }
    header_b64 = _b64encode(json.dumps(header, separators=(",", ":")).encode())
    payload_b64 = _b64encode(json.dumps(payload, separators=(",", ":")).encode())
    signing_input = f"{header_b64}.{payload_b64}".encode()
    return f"{header_b64}.{payload_b64}.{_sign(signing_input)}"


def decode_access_token(token: str) -> dict | None:
    try:
        header_b64, payload_b64, signature = token.split(".")
    except ValueError:
        return None
    signing_input = f"{header_b64}.{payload_b64}".encode()
    if not hmac.compare_digest(_sign(signing_input), signature):
        return None
    try:
        payload: dict = json.loads(_b64decode(payload_b64))
    except (ValueError, json.JSONDecodeError):
        return None
    if int(payload.get("exp", 0)) < int(time.time()):
        return None
    return payload
