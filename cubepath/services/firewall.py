from __future__ import annotations

from typing import TYPE_CHECKING, Any

from cubepath.models.firewall import (
    CreateFirewallGroupRequest,
    FirewallGroup,
    UpdateFirewallGroupRequest,
    VPSFirewallGroupsRequest,
    VPSFirewallGroupsResponse,
)

if TYPE_CHECKING:
    from cubepath.client import CubePathClient


class FirewallService:
    def __init__(self, client: CubePathClient) -> None:
        self._client = client

    def create(self, req: CreateFirewallGroupRequest) -> FirewallGroup:
        data: dict[str, Any] = self._client.post("/firewall/groups", json=req.to_dict())
        return FirewallGroup.from_dict(data)

    def list(self) -> list[FirewallGroup]:
        data: list[dict[str, Any]] = self._client.get("/firewall/groups")
        return [FirewallGroup.from_dict(g) for g in data]

    def get(self, group_id: str) -> FirewallGroup:
        data: dict[str, Any] = self._client.get(f"/firewall/groups/{group_id}")
        return FirewallGroup.from_dict(data)

    def update(self, group_id: str, req: UpdateFirewallGroupRequest) -> FirewallGroup:
        data: dict[str, Any] = self._client.patch(f"/firewall/groups/{group_id}", json=req.to_dict())
        return FirewallGroup.from_dict(data)

    def delete(self, group_id: str) -> None:
        self._client.delete(f"/firewall/groups/{group_id}")

    def assign_to_vps(self, vps_id: str, req: VPSFirewallGroupsRequest) -> VPSFirewallGroupsResponse:
        data: dict[str, Any] = self._client.post(f"/vps/{vps_id}/firewall-groups", json=req.to_dict())
        return VPSFirewallGroupsResponse.from_dict(data)
