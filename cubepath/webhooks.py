"""Verification of Object Storage event webhook deliveries."""

from __future__ import annotations

import hashlib
import hmac
import re
import time

__all__ = ["StorageEventSignatureError", "verify_storage_event_signature"]

_HEX64 = re.compile(r"^[0-9a-fA-F]{64}$")


class StorageEventSignatureError(Exception):
    """Raised when a storage event delivery must not be trusted."""


def verify_storage_event_signature(
    secret: str,
    timestamp: str,
    body: bytes | str,
    header: str,
    tolerance: float = 300,
    *,
    now: float | None = None,
) -> None:
    """Verify an Object Storage event webhook delivery.

    ``secret`` is the signing secret of the destination, ``timestamp`` the CubePath-Timestamp
    header (unix seconds), ``body`` the raw request body (verify before parsing it) and ``header``
    the CubePath-Signature header: one or more ``v1=<hex>`` values (``v1=<new>, v1=<previous>``
    during a secret rotation), each the HMAC-SHA256 of ``timestamp + "." + body``. Deliveries whose timestamp is
    further than ``tolerance`` seconds (default 300) from now are rejected; 0 skips that check.

    Raises StorageEventSignatureError when the delivery is not valid.
    """
    ts = (timestamp or "").strip()
    if not ts.isdigit():
        raise StorageEventSignatureError("Invalid timestamp")
    current = time.time() if now is None else now
    if tolerance > 0 and abs(current - int(ts)) > tolerance:
        raise StorageEventSignatureError("Timestamp outside the tolerance")
    raw = body.encode() if isinstance(body, str) else body
    expected = hmac.new(secret.encode(), ts.encode() + b"." + raw, hashlib.sha256).hexdigest()
    for part in re.split(r"[,\s]+", header or ""):
        if not part.startswith("v1="):
            continue
        value = part[3:].lower()
        if _HEX64.match(value) and hmac.compare_digest(value, expected):
            return
    raise StorageEventSignatureError("Storage event signature mismatch")
