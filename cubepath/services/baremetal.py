from __future__ import annotations

import builtins
from typing import TYPE_CHECKING, Any

from cubepath.exceptions import APIError
from cubepath.models.baremetal import (
    Baremetal,
    BaremetalKVM,
    BaremetalModelLocation,
    BaremetalOSOption,
    BMCSensors,
    CreateBaremetalRequest,
    IPMISession,
    ReinstallBaremetalRequest,
    ReinstallStatus,
    RescueResponse,
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
                if str(bm.get("id")) == str(baremetal_id):
                    return Baremetal.from_dict(bm)
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
        """Temperatures and fan speeds from the last BMC poll, served through GraphQL."""
        data = self._client.graphql(
            "query($id: ID!) { baremetal(id: $id) { sensors { ipmiAvailable powerOn lastSeen "
            "temperatures { name value unit } fans { name value unit } } } }",
            {"id": str(baremetal_id)},
        )
        if not data.get("baremetal"):
            raise APIError(404, "Not Found", f"baremetal {baremetal_id} not found")
        s = data["baremetal"]["sensors"]
        return BMCSensors.from_dict(
            {
                "ipmi_available": bool(s.get("ipmiAvailable")),
                "power_on": bool(s.get("powerOn")),
                "last_seen": s.get("lastSeen"),
                "sensors": {"temperatures": s.get("temperatures") or [], "fans": s.get("fans") or []},
            }
        )

    def ipmi_session(self, baremetal_id: str) -> IPMISession:
        data: dict[str, Any] = self._client.post(f"/ipmi-proxy/create-session/{baremetal_id}")
        return IPMISession.from_dict(data)

    def reinstall(self, baremetal_id: str, req: ReinstallBaremetalRequest) -> None:
        self._client.post(f"/baremetal/{baremetal_id}/reinstall", json=req.to_dict())

    def reinstall_status(self, baremetal_id: str) -> ReinstallStatus:
        """Whether an OS reinstallation is running.

        There is no dedicated endpoint any more: a server is reinstalling while its status is
        ``deploying``.
        """
        bm = self.get(baremetal_id)
        return ReinstallStatus(is_reinstalling=bm.status == "deploying", status=bm.status)

    def cancel_reinstall(self, baremetal_id: str) -> None:
        """Cancel a pending or running OS reinstallation."""
        self._client.delete(f"/baremetal/{baremetal_id}/reinstall")

    def monitoring_enable(self, baremetal_id: str) -> None:
        self._client.put(f"/baremetal/{baremetal_id}/monitoring", params={"enable": "true"})

    def monitoring_disable(self, baremetal_id: str) -> None:
        self._client.put(f"/baremetal/{baremetal_id}/monitoring", params={"enable": "false"})

    def list_models(self) -> builtins.list[BaremetalModelLocation]:
        """Server models by location, with price and stock."""
        data: dict[str, Any] = self._client.get("/baremetal/models")
        return [BaremetalModelLocation.from_dict(loc) for loc in data.get("locations", [])]

    def list_os(self, baremetal_id: str) -> builtins.list[BaremetalOSOption]:
        """Operating systems and disk layouts that can be installed on the server."""
        data: list[dict[str, Any]] = self._client.get(f"/baremetal/os/{baremetal_id}")
        return [BaremetalOSOption.from_dict(o) for o in data]

    def kvm(self, baremetal_id: str) -> BaremetalKVM:
        """KVM-over-IP console URL and credentials, for servers that have one."""
        data: dict[str, Any] = self._client.get(f"/baremetal/{baremetal_id}/kvm")
        return BaremetalKVM.from_dict(data)

    def configure_protection(self, baremetal_id: str, enabled: bool) -> None:
        """A protected server cannot be reinstalled."""
        self._client.post(f"/baremetal/{baremetal_id}/protection", json={"enabled": enabled})

    def move_to_project(self, baremetal_id: str, project_id: int) -> None:
        self._client.post(f"/baremetal/{baremetal_id}/move-project", json={"project_id": project_id})

    def add_ssh_keys(self, baremetal_id: str, ssh_key_ids: builtins.list[int]) -> None:
        """Authorise more SSH keys on the server."""
        self._client.post(f"/baremetal/{baremetal_id}/ssh-keys", json=ssh_key_ids)

    def remove_ssh_key(self, baremetal_id: str, ssh_key_id: int | str) -> None:
        self._client.delete(f"/baremetal/{baremetal_id}/ssh-keys/{ssh_key_id}")

    def attach_network(self, baremetal_id: str, network_id: int) -> None:
        """Attach a private network to the server."""
        self._client.post(f"/baremetal/{baremetal_id}/network", json={"network_id": network_id})

    def detach_network(self, baremetal_id: str) -> None:
        self._client.delete(f"/baremetal/{baremetal_id}/network")
