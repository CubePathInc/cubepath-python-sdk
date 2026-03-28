from __future__ import annotations

from typing import TYPE_CHECKING, Any

from cubepath.models.baremetal import (
    BMCSensors, Baremetal, CreateBaremetalRequest, IPMISession,
    ReinstallBaremetalRequest, ReinstallStatus, RescueResponse,
    UpdateBaremetalRequest,
)
from cubepath.models.projects import ProjectResponse
from cubepath.models.vps import TaskResponse

if TYPE_CHECKING:
    from cubepath.client import CubePathClient


class BaremetalService:
    def __init__(self, client: CubePathClient) -> None:
        self._client = client

    def deploy(self, project_id: str, req: CreateBaremetalRequest) -> TaskResponse:
        data: dict[str, Any] = self._client.post(f"/baremetal/deploy/{project_id}", json=req.to_dict())
        return TaskResponse.from_dict(data)

    def list(self) -> list[ProjectResponse]:
        data: list[dict[str, Any]] = self._client.get("/projects/")
        return [ProjectResponse.from_dict(p) for p in data]

    def get(self, baremetal_id: str) -> Baremetal:
        projects: list[dict[str, Any]] = self._client.get("/projects/")
        for proj in projects:
            for bm in proj.get("baremetals", []):
                if bm.get("id") == baremetal_id:
                    return Baremetal.from_dict(bm)
        from cubepath.exceptions import APIError
        raise APIError(404, "Not Found", f"baremetal {baremetal_id} not found")

    def update(self, baremetal_id: str, req: UpdateBaremetalRequest) -> None:
        self._client.patch(f"/baremetal/update/{baremetal_id}", json=req.to_dict())

    def power(self, baremetal_id: str, action: str) -> None:
        self._client.post(f"/baremetal/{baremetal_id}/power/{action}")

    def rescue(self, baremetal_id: str) -> RescueResponse:
        data: dict[str, Any] = self._client.post(f"/baremetal/{baremetal_id}/rescue")
        return RescueResponse.from_dict(data)

    def reset_bmc(self, baremetal_id: str) -> None:
        self._client.post(f"/baremetal/{baremetal_id}/reset-bmc")

    def bmc_sensors(self, baremetal_id: str) -> BMCSensors:
        data: dict[str, Any] = self._client.get(f"/baremetal/{baremetal_id}/bmc-sensors")
        return BMCSensors.from_dict(data)

    def ipmi_session(self, baremetal_id: str) -> IPMISession:
        data: dict[str, Any] = self._client.post(f"/ipmi-proxy/create-session/{baremetal_id}")
        return IPMISession.from_dict(data)

    def reinstall(self, baremetal_id: str, req: ReinstallBaremetalRequest) -> None:
        self._client.post(f"/baremetal/{baremetal_id}/reinstall", json=req.to_dict())

    def reinstall_status(self, baremetal_id: str) -> ReinstallStatus:
        data: dict[str, Any] = self._client.get(f"/baremetal/{baremetal_id}/reinstall/status")
        return ReinstallStatus.from_dict(data)

    def monitoring_enable(self, baremetal_id: str) -> None:
        self._client.put(f"/baremetal/{baremetal_id}/monitoring", json={"enable": True})

    def monitoring_disable(self, baremetal_id: str) -> None:
        self._client.put(f"/baremetal/{baremetal_id}/monitoring", json={"enable": False})
