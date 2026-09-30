from __future__ import annotations

from typing import TYPE_CHECKING, Any

from cubepath.exceptions import APIError
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
        if not req.project_id:
            raise ValueError("project_id is required to create a firewall group")
        data: dict[str, Any] = self._client.post(
            "/firewall/groups", json=req.to_dict(), params={"project_id": req.project_id}
        )
        return FirewallGroup.from_dict(data)

    def list(self) -> list[FirewallGroup]:
        data: list[dict[str, Any]] = self._client.get("/firewall/groups")
        return [FirewallGroup.from_dict(g) for g in data]

    def get(self, group_id: str) -> FirewallGroup:
        """The API has no single-group endpoint, so the group is looked up in the list."""
        for group in self.list():
            if str(group.id) == str(group_id):
                return group
        raise APIError(404, "Not Found", f"firewall group {group_id} not found")

    def update(self, group_id: str, req: UpdateFirewallGroupRequest) -> FirewallGroup:
        """Change the name, rules or enabled flag; unset fields are left unchanged."""
        data: dict[str, Any] = self._client.put(f"/firewall/groups/{group_id}", json=req.to_dict())
        return FirewallGroup.from_dict(data)

    def delete(self, group_id: str) -> None:
        self._client.delete(f"/firewall/groups/{group_id}")

    def assign_to_vps(self, vps_id: str, req: VPSFirewallGroupsRequest) -> VPSFirewallGroupsResponse:
        """Replace the firewall groups of a VPS (at most 10, in priority order).

        An empty list removes them all. The new rules are applied in the background.
        """
        data: dict[str, Any] = self._client.put(f"/firewall/vps/{vps_id}/groups", json=req.to_dict())
        return VPSFirewallGroupsResponse.from_dict(data)
