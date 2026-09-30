from __future__ import annotations

import builtins
from typing import TYPE_CHECKING, Any

from cubepath.models.networks import (
    BGPPeer,
    CreateBGPPeerRequest,
    CreateNetworkRequest,
    CreateNetworkRouteRequest,
    Network,
    NetworkRoute,
    UpdateBGPPeerRequest,
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

    def move_to_project(self, network_id: str, project_id: int) -> None:
        self._client.post(f"/networks/{network_id}/move-project", json={"project_id": project_id})

    # ── BGP peers ────────────────────────────────────────────────

    def list_bgp_peers(self, network_id: str) -> builtins.list[BGPPeer]:
        data: list[dict[str, Any]] = self._client.get(f"/networks/{network_id}/bgp-peers")
        return [BGPPeer.from_dict(p) for p in data]

    def create_bgp_peer(self, network_id: str, req: CreateBGPPeerRequest) -> BGPPeer:
        """Peer the network's router with a server of the network or an IP, to learn routes over BGP."""
        data: dict[str, Any] = self._client.post(f"/networks/{network_id}/bgp-peers", json=req.to_dict())
        return BGPPeer.from_dict(data)

    def update_bgp_peer(self, network_id: str, peer_id: str, req: UpdateBGPPeerRequest) -> None:
        self._client.patch(f"/networks/{network_id}/bgp-peers/{peer_id}", json=req.to_dict())

    def delete_bgp_peer(self, network_id: str, peer_id: str) -> None:
        self._client.delete(f"/networks/{network_id}/bgp-peers/{peer_id}")
