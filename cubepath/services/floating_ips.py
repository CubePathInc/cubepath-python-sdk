from __future__ import annotations

from typing import TYPE_CHECKING, Any

from cubepath.models.floating_ips import FloatingIP, FloatingIPsResponse

if TYPE_CHECKING:
    from cubepath.client import CubePathClient


class FloatingIPService:
    def __init__(self, client: CubePathClient) -> None:
        self._client = client

    def list(self) -> FloatingIPsResponse:
        data: dict[str, Any] = self._client.get("/floating_ips/organization")
        return FloatingIPsResponse.from_dict(data)

    def acquire(self, ip_type: str, location_name: str) -> FloatingIP:
        data: dict[str, Any] = self._client.post(
            "/floating_ips/acquire",
            params={"ip_type": ip_type, "location_name": location_name},
        )
        return FloatingIP.from_dict(data)

    def release(self, address: str) -> None:
        self._client.post(f"/floating_ips/release/{address}")

    def assign(self, resource_type: str, resource_id: str, address: str) -> None:
        self._client.post(
            f"/floating_ips/assign/{resource_type}/{resource_id}",
            params={"address": address},
        )

    def unassign(self, address: str) -> None:
        self._client.post(f"/floating_ips/unassign/{address}")

    def configure_reverse_dns(self, ip: str, reverse_dns: str) -> None:
        self._client.post(
            "/floating_ips/reverse_dns/configure",
            params={"ip": ip, "reverse_dns": reverse_dns},
        )
