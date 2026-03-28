from __future__ import annotations

from typing import TYPE_CHECKING, Any

from cubepath.models.pricing import PricingResponse

if TYPE_CHECKING:
    from cubepath.client import CubePathClient


class PricingService:
    def __init__(self, client: CubePathClient) -> None:
        self._client = client

    def get(self) -> PricingResponse:
        data: dict[str, Any] = self._client.get("/pricing")
        return PricingResponse.from_dict(data)
