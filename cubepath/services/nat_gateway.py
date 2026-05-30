from __future__ import annotations

from typing import TYPE_CHECKING, Any

from cubepath.models.nat_gateway import (
    CreateNATGatewayRequest,
    NATGateway,
    NATGatewayLocationPlans,
    UpdateNATGatewayRequest,
)

if TYPE_CHECKING:
    from cubepath.client import CubePathClient


class NATGatewayService:
    def __init__(self, client: CubePathClient) -> None:
        self._client = client

    def list_plans(self) -> list[NATGatewayLocationPlans]:
        data: list[dict[str, Any]] = self._client.get("/nat-gateway/plans")
        return [NATGatewayLocationPlans.from_dict(lp) for lp in data]

    def list(self) -> list[NATGateway]:
        data: list[dict[str, Any]] = self._client.get("/nat-gateway/")
        return [NATGateway.from_dict(gw) for gw in data]

    def get(self, uuid: str) -> NATGateway:
        data: dict[str, Any] = self._client.get(f"/nat-gateway/{uuid}")
        return NATGateway.from_dict(data)

    def create(self, req: CreateNATGatewayRequest) -> NATGateway:
        data: dict[str, Any] = self._client.post("/nat-gateway/", json=req.to_dict())
        return NATGateway.from_dict(data)

    def update(self, uuid: str, req: UpdateNATGatewayRequest) -> NATGateway:
        data: dict[str, Any] = self._client.patch(f"/nat-gateway/{uuid}", json=req.to_dict())
        return NATGateway.from_dict(data)

    def delete(self, uuid: str) -> None:
        self._client.delete(f"/nat-gateway/{uuid}")

    def resize(self, uuid: str, plan_name: str) -> None:
        self._client.post(f"/nat-gateway/{uuid}/resize", json={"plan_name": plan_name})

    def move_to_project(self, uuid: str, project_id: int) -> None:
        self._client.post(f"/nat-gateway/{uuid}/move-to-project", json={"project_id": project_id})

    def configure_protection(self, uuid: str, enabled: bool) -> None:
        self._client.post(f"/nat-gateway/{uuid}/protection", json={"enabled": enabled})

    def get_metrics(self, uuid: str) -> dict[str, Any]:
        result: dict[str, Any] = self._client.get(f"/nat-gateway/{uuid}/metrics")
        return result

    def get_bandwidth_usage(self, uuid: str) -> dict[str, Any]:
        result: dict[str, Any] = self._client.get(f"/nat-gateway/{uuid}/bandwidth-usage")
        return result
