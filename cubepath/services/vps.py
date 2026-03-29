from __future__ import annotations

from typing import TYPE_CHECKING, Any

from cubepath.models.projects import ProjectResponse
from cubepath.models.vps import (
    VPS,
    CreateVPSBackupRequest,
    CreateVPSRequest,
    ISOListResponse,
    TaskResponse,
    UpdateVPSBackupSettingsRequest,
    UpdateVPSRequest,
    VPSBackup,
    VPSBackupSettings,
    VPSTemplatesResponse,
)

if TYPE_CHECKING:
    from cubepath.client import CubePathClient


class VPSBackupService:
    def __init__(self, client: CubePathClient) -> None:
        self._client = client

    def list(self, vps_id: str) -> list[VPSBackup]:
        data: list[dict[str, Any]] = self._client.get(f"/vps/{vps_id}/backups")
        return [VPSBackup.from_dict(b) for b in data]

    def create(self, vps_id: str, req: CreateVPSBackupRequest | None = None) -> None:
        self._client.post(f"/vps/{vps_id}/backups", json=req.to_dict() if req else {})

    def restore(self, vps_id: str, backup_id: str) -> None:
        self._client.post(f"/vps/{vps_id}/backups/{backup_id}/restore")

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


class VPSService:
    def __init__(self, client: CubePathClient) -> None:
        self._client = client
        self._backups = VPSBackupService(client)
        self._isos = VPSISOService(client)

    def backups(self) -> VPSBackupService:
        return self._backups

    def isos(self) -> VPSISOService:
        return self._isos

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

    def destroy(self, vps_id: str, release_ips: bool = False) -> None:
        params = {"release_ips": str(release_ips).lower()} if release_ips else None
        self._client.post(f"/vps/destroy/{vps_id}", params=params)

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
