from __future__ import annotations

import builtins
from typing import TYPE_CHECKING, Any

from cubepath.models.networks import (
    CreateNetworkRequest,
    CreateNetworkRouteRequest,
    Network,
    NetworkRoute,
    UpdateNetworkRequest,
)
from cubepath.models.projects import ProjectResponse

if TYPE_CHECKING:
    from cubepath.client import CubePathClient


class NetworkService:
    def __init__(self, client: CubePathClient) -> None:
        self._client = client

    def create(self, req: CreateNetworkRequest) -> Network:
        data: dict[str, Any] = self._client.post("/networks/create_network", json=req.to_dict())
        return Network.from_dict(data)

    def list(self) -> list[ProjectResponse]:
        data: list[dict[str, Any]] = self._client.get("/projects/")
        return [ProjectResponse.from_dict(p) for p in data]

    def update(self, network_id: str, req: UpdateNetworkRequest) -> None:
        self._client.put(f"/networks/{network_id}", json=req.to_dict())

    def delete(self, network_id: str) -> None:
        self._client.delete(f"/networks/{network_id}")

    def list_routes(self, network_id: str) -> builtins.list[NetworkRoute]:
        data: list[dict[str, Any]] = self._client.get(f"/networks/{network_id}/routes")
        return [NetworkRoute.from_dict(r) for r in data]

    def create_route(self, network_id: str, req: CreateNetworkRouteRequest) -> NetworkRoute:
        data: dict[str, Any] = self._client.post(f"/networks/{network_id}/routes", json=req.to_dict())
        return NetworkRoute.from_dict(data)

    def delete_route(self, network_id: str, route_id: str) -> None:
        self._client.delete(f"/networks/{network_id}/routes/{route_id}")
