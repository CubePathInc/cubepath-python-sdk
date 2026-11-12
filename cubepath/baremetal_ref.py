"""How a baremetal server is named: its uuid.

The ``id`` of a baremetal is its uuid (``uuid`` carries the same value). Every ``/baremetal/{uuid}`` route,
and every field that names a server inside other objects (route next hop, BGP peer target, load balancer
target, alert target id, floating IP assignment), takes the uuid. The client validates the reference once,
before any request, and sends it in lower case. A server number is not a reference any more.
"""

from __future__ import annotations

import re
from typing import Any

__all__ = ["baremetal_ref", "baremetal_matches", "baremetal_target"]

_UUID = re.compile(r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}")


def baremetal_ref(value: Any) -> str:
    """Validate a baremetal reference and return it in lower case.

    Accepts a uuid in any case. Anything else, a server number included, raises ``ValueError`` and is never
    sent.
    """
    if isinstance(value, str):
        lowered = value.lower()
        if _UUID.fullmatch(lowered):
            return lowered
    raise ValueError(f"baremetal reference must be a uuid (8-4-4-4-12 hex), got {value!r}")


def baremetal_target(target_type: str | None, target: Any) -> Any:
    """Validate the target of a route, BGP peer, load balancer target or alert when it is a baremetal.

    A baremetal target must be a uuid (returned in lower case); targets of other types are returned as given.
    """
    if target_type == "baremetal":
        return baremetal_ref(target)
    return target


def baremetal_matches(item: dict[str, Any], ref: str) -> bool:
    """Whether a baremetal object of a listing is the one ``ref`` (already validated) names."""
    item_id = item.get("id")
    return isinstance(item_id, str) and item_id.lower() == ref
