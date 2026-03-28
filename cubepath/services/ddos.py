from __future__ import annotations

from typing import TYPE_CHECKING, Any

from cubepath.models.ddos import DDoSAttack

if TYPE_CHECKING:
    from cubepath.client import CubePathClient


class DDoSService:
    def __init__(self, client: CubePathClient) -> None:
        self._client = client

    def list_attacks(self) -> list[DDoSAttack]:
        data: list[dict[str, Any]] = self._client.get("/ddos-attacks/attacks")
        return [DDoSAttack.from_dict(a) for a in data]
