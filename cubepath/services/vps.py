from __future__ import annotations

import builtins
from typing import TYPE_CHECKING, Any

from cubepath.models.projects import ProjectResponse
from cubepath.models.vps import (
    VPS,
    AvailabilityGroup,
    CreateAvailabilityGroupRequest,
    CreateVPSBackupRequest,
    CreateVPSRequest,
    ISOListResponse,
    TaskResponse,
    UpdateVPSBackupSettingsRequest,
    UpdateVPSRequest,
    VPSBackup,
    VPSBackupList,
    VPSBackupSettings,
    VPSConsole,
    VPSLocationPlans,
    VPSTemplatesResponse,
)

if TYPE_CHECKING:
    from cubepath.client import CubePathClient


class VPSBackupService:
    def __init__(self, client: CubePathClient) -> None:
        self._client = client

    def list(self, vps_id: str) -> list[VPSBackup]:
        return self.list_with_settings(vps_id).backups

    def list_with_settings(self, vps_id: str) -> VPSBackupList:
        """Backups of the server plus its automatic backup settings."""
        data: dict[str, Any] = self._client.get(f"/vps/{vps_id}/backups")
        return VPSBackupList.from_dict(data)

    def create(self, vps_id: str, req: CreateVPSBackupRequest | None = None) -> VPSBackup:
        """Start a manual backup; it is ready once its status is completed."""
        data: dict[str, Any] = self._client.post(f"/vps/{vps_id}/backups", json=req.to_dict() if req else {})
        return VPSBackup.from_dict(data)

    def restore(self, vps_id: str, backup_id: str) -> None:
        """Overwrite the server's disk with the backup."""
        self._client.post(f"/vps/{vps_id}/backups/{backup_id}/restore", json={"confirm": True})

    def delete(self, vps_id: str, backup_id: str) -> None:
        self._client.delete(f"/vps/{vps_id}/backups/{backup_id}")

    def get_settings(self, vps_id: str) -> VPSBackupSettings:
        data: dict[str, Any] = self._client.get(f"/vps/{vps_id}/backup/settings")
        return VPSBackupSettings.from_dict(data)

    def update_settings(self, vps_id: str, req: UpdateVPSBackupSettingsRequest) -> None:
        self._client.put(f"/vps/{vps_id}/backup/settings", json=req.to_dict())


class VPSISOService:
    def __init__(self, client: CubePathClient) -> None:
        self._client = client

    def list(self, vps_id: str) -> ISOListResponse:
        data: dict[str, Any] = self._client.get(f"/vps/{vps_id}/isos")
        return ISOListResponse.from_dict(data)

    def mount(self, vps_id: str, iso_id: str) -> None:
        self._client.post(f"/vps/{vps_id}/iso", json={"iso_id": iso_id})

    def unmount(self, vps_id: str) -> None:
        self._client.delete(f"/vps/{vps_id}/iso")


class AvailabilityGroupService:
    """Spread groups: the servers of a group run on different hosts."""

    def __init__(self, client: CubePathClient) -> None:
        self._client = client

    def list(self, project_id: int | str, location_name: str | None = None) -> list[AvailabilityGroup]:
        data: dict[str, Any] = self._client.get(
            f"/vps/availability-groups/project/{project_id}",
            params={"location_name": location_name} if location_name else None,
        )
        return [AvailabilityGroup.from_dict(g) for g in data.get("groups", [])]

    def get(self, group_uuid: str) -> AvailabilityGroup:
        data: dict[str, Any] = self._client.get(f"/vps/availability-groups/{group_uuid}")
        return AvailabilityGroup.from_dict(data)

    def create(self, req: CreateAvailabilityGroupRequest) -> AvailabilityGroup:
        data: dict[str, Any] = self._client.post("/vps/availability-groups/", json=req.to_dict())
        return AvailabilityGroup.from_dict(data)

    def delete(self, group_uuid: str) -> None:
        """Delete an empty group."""
        self._client.delete(f"/vps/availability-groups/{group_uuid}")

    def add_vps(self, group_uuid: str, vps_id: int | str) -> None:
        self._client.post(f"/vps/availability-groups/{group_uuid}/vps/{vps_id}")

    def remove_vps(self, group_uuid: str, vps_id: int | str) -> None:
        self._client.delete(f"/vps/availability-groups/{group_uuid}/vps/{vps_id}")

    def move_to_project(self, group_uuid: str, project_id: int) -> None:
        """Move the group and its servers to another project of the organization."""
        self._client.post(f"/vps/availability-groups/{group_uuid}/move-project", json={"project_id": project_id})


class VPSService:
    def __init__(self, client: CubePathClient) -> None:
        self._client = client
        self._backups = VPSBackupService(client)
        self._isos = VPSISOService(client)
        self._availability_groups = AvailabilityGroupService(client)

    def backups(self) -> VPSBackupService:
        return self._backups

    def isos(self) -> VPSISOService:
        return self._isos

    def availability_groups(self) -> AvailabilityGroupService:
        return self._availability_groups

    def create(self, project_id: str, req: CreateVPSRequest) -> TaskResponse:
        data: dict[str, Any] = self._client.post(f"/vps/create/{project_id}", json=req.to_dict())
        return TaskResponse.from_dict(data)

    def list(self) -> list[ProjectResponse]:
        data: list[dict[str, Any]] = self._client.get("/projects/")
        return [ProjectResponse.from_dict(p) for p in data]

    def get(self, vps_id: str) -> VPS:
        projects: list[dict[str, Any]] = self._client.get("/projects/")
        for proj in projects:
            for v in proj.get("vps", []):
                if v.get("id") == vps_id:
                    return VPS.from_dict(v)
        from cubepath.exceptions import APIError

        raise APIError(404, "Not Found", f"vps {vps_id} not found")

    def destroy(self, vps_id: str, release_ips: bool = True) -> None:
        """Destroy the server. With release_ips=False its floating IPs stay in the organization."""
        self._client.post(f"/vps/destroy/{vps_id}", json={"release_ips": release_ips})

    def update(self, vps_id: str, req: UpdateVPSRequest) -> None:
        self._client.patch(f"/vps/update/{vps_id}", json=req.to_dict())

    def resize(self, vps_id: str, plan_name: str) -> None:
        self._client.post(f"/vps/resize/vps_id/{vps_id}/resize_plan/{plan_name}")

    def change_password(self, vps_id: str, password: str) -> None:
        self._client.post(f"/vps/{vps_id}/change-password", json={"password": password})

    def reinstall(self, vps_id: str, template_name: str) -> None:
        self._client.post(f"/vps/reinstall/{vps_id}", json={"template_name": template_name})

    def power(self, vps_id: str, action: str) -> None:
        self._client.post(f"/vps/{vps_id}/power/{action}")

    def templates(self) -> VPSTemplatesResponse:
        data: dict[str, Any] = self._client.get("/vps/templates")
        return VPSTemplatesResponse.from_dict(data)

    def plans(self) -> builtins.list[VPSLocationPlans]:
        """Available plans by location and cluster, with their price."""
        data: dict[str, Any] = self._client.get("/vps/plans")
        return [VPSLocationPlans.from_dict(loc) for loc in data.get("locations", [])]

    def configure_protection(self, vps_id: str, enabled: bool) -> None:
        """A protected server cannot be destroyed, reinstalled or restored."""
        self._client.post(f"/vps/{vps_id}/protection", json={"enabled": enabled})

    def move_to_project(self, vps_id: str, project_id: int) -> None:
        self._client.post(f"/vps/{vps_id}/move-project", json={"project_id": project_id})

    def add_ssh_keys(self, vps_id: str, ssh_key_ids: builtins.list[int]) -> None:
        """Authorise more SSH keys on the server."""
        self._client.post(f"/vps/{vps_id}/ssh-keys", json=ssh_key_ids)

    def remove_ssh_key(self, vps_id: str, ssh_key_id: int | str) -> None:
        self._client.delete(f"/vps/{vps_id}/ssh-keys/{ssh_key_id}")

    def attach_network(self, vps_id: str, network_id: int) -> None:
        """Attach a private network; restart the server to apply it."""
        self._client.post(f"/vps/{vps_id}/network", json={"network_id": network_id})

    def detach_network(self, vps_id: str) -> None:
        self._client.delete(f"/vps/{vps_id}/network")

    def console(self, vps_id: str) -> VPSConsole:
        """Open a VNC console session (noVNC websocket URL and ticket)."""
        data: dict[str, Any] = self._client.post(f"/vps/{vps_id}/vnc-url")
        return VPSConsole.from_dict(data)
