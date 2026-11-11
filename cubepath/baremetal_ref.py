"""How a baremetal server is named: its number or its uuid.

The public ``id`` of a baremetal stays the number and a ``uuid`` is added next to it. Every
``/baremetal/{ref}`` route accepts either form, so the client validates the reference once, before any
request, and passes it through to the URL as given (the number as digits, the uuid in lower case).

The echo fields (route next hop, BGP peer target, load balancer target, alert target id) take only the
server **number**: pass ``baremetal.id`` there, never the uuid.
"""

from __future__ import annotations

import re
from typing import Any

__all__ = ["baremetal_ref", "baremetal_matches"]

_NUMBER = re.compile(r"[0-9]+")
_UUID = re.compile(r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}")


def baremetal_ref(value: Any) -> str:
    """Validate a baremetal reference and return the text to put in the URL.

    Accepts an ``int`` or a string of ASCII digits (returned as given) and a uuid in any case (returned in
    lower case). Anything else raises ``ValueError``: it is never cast to ``int`` and never sent.
    """
    if isinstance(value, bool):
        raise ValueError("baremetal reference must be a number or a uuid, got a bool")
    if isinstance(value, int):
        if value < 0:
            raise ValueError(f"baremetal reference must be a number or a uuid, got {value!r}")
        return str(value)
    if isinstance(value, str):
        if _NUMBER.fullmatch(value):
            return value
        lowered = value.lower()
        if _UUID.fullmatch(lowered):
            return lowered
    raise ValueError(f"baremetal reference must be a number or a uuid (8-4-4-4-12 hex), got {value!r}")


def baremetal_matches(item: dict[str, Any], ref: str) -> bool:
    """Whether a baremetal object of a listing is the one ``ref`` (already validated) names.

    ``id`` may come as a number or as numeric text; ``uuid`` is absent on an API from before the uuid.
    """
    if str(item.get("id", "")) == ref:
        return True
    uuid = item.get("uuid")
    return isinstance(uuid, str) and uuid != "" and uuid.lower() == ref
