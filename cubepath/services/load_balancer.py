from __future__ import annotations

import builtins
from typing import TYPE_CHECKING, Any

from cubepath.models.load_balancer import (
    AddTargetRequest,
    CreateListenerRequest,
    CreateLoadBalancerRequest,
    HealthCheckConfig,
    LBListener,
    LBLocationPlans,
    LBTarget,
    LoadBalancer,
    UpdateListenerRequest,
    UpdateLoadBalancerRequest,
    UpdateTargetRequest,
)

if TYPE_CHECKING:
    from cubepath.client import CubePathClient


class LoadBalancerService:
    def __init__(self, client: CubePathClient) -> None:
        self._client = client

    # ── Load Balancers ───────────────────────────────────────────

    def list(self) -> list[LoadBalancer]:
        data: list[dict[str, Any]] = self._client.get("/loadbalancer/")
        return [LoadBalancer.from_dict(lb) for lb in data]

    def get(self, lb_uuid: str) -> LoadBalancer:
        data: dict[str, Any] = self._client.get(f"/loadbalancer/{lb_uuid}")
        return LoadBalancer.from_dict(data)

    def create(self, req: CreateLoadBalancerRequest) -> LoadBalancer:
        data: dict[str, Any] = self._client.post("/loadbalancer/", json=req.to_dict())
        return LoadBalancer.from_dict(data)

    def update(self, lb_uuid: str, req: UpdateLoadBalancerRequest) -> LoadBalancer:
        data: dict[str, Any] = self._client.patch(f"/loadbalancer/{lb_uuid}", json=req.to_dict())
        return LoadBalancer.from_dict(data)

    def delete(self, lb_uuid: str) -> None:
        self._client.delete(f"/loadbalancer/{lb_uuid}")

    def resize(self, lb_uuid: str, plan_name: str) -> None:
        self._client.post(f"/loadbalancer/{lb_uuid}/resize", json={"plan_name": plan_name})

    def list_plans(self) -> builtins.list[LBLocationPlans]:
        data = self._client.get("/loadbalancer/plans")
        return [LBLocationPlans.from_dict(lp) for lp in data]

    # ── Listeners ────────────────────────────────────────────────

    def create_listener(self, lb_uuid: str, req: CreateListenerRequest) -> LBListener:
        data: dict[str, Any] = self._client.post(f"/loadbalancer/{lb_uuid}/listeners", json=req.to_dict())
        return LBListener.from_dict(data)

    def update_listener(self, lb_uuid: str, listener_uuid: str, req: UpdateListenerRequest) -> LBListener:
        data: dict[str, Any] = self._client.patch(
            f"/loadbalancer/{lb_uuid}/listeners/{listener_uuid}",
            json=req.to_dict(),
        )
        return LBListener.from_dict(data)

    def delete_listener(self, lb_uuid: str, listener_uuid: str) -> None:
        self._client.delete(f"/loadbalancer/{lb_uuid}/listeners/{listener_uuid}")

    # ── Targets ──────────────────────────────────────────────────

    def add_target(self, lb_uuid: str, listener_uuid: str, req: AddTargetRequest) -> LBTarget:
        data: dict[str, Any] = self._client.post(
            f"/loadbalancer/{lb_uuid}/listeners/{listener_uuid}/targets",
            json=req.to_dict(),
        )
        return LBTarget.from_dict(data)

    def update_target(
        self,
        lb_uuid: str,
        listener_uuid: str,
        target_uuid: str,
        req: UpdateTargetRequest,
    ) -> LBTarget:
        data: dict[str, Any] = self._client.patch(
            f"/loadbalancer/{lb_uuid}/listeners/{listener_uuid}/targets/{target_uuid}",
            json=req.to_dict(),
        )
        return LBTarget.from_dict(data)

    def remove_target(self, lb_uuid: str, listener_uuid: str, target_uuid: str) -> None:
        self._client.delete(f"/loadbalancer/{lb_uuid}/listeners/{listener_uuid}/targets/{target_uuid}")

    def drain_target(self, lb_uuid: str, listener_uuid: str, target_uuid: str) -> None:
        self._client.post(
            f"/loadbalancer/{lb_uuid}/listeners/{listener_uuid}/targets/{target_uuid}/drain",
        )

    # ── Health Checks ────────────────────────────────────────────

    def configure_health_check(self, lb_uuid: str, listener_uuid: str, req: HealthCheckConfig) -> None:
        self._client.put(
            f"/loadbalancer/{lb_uuid}/listeners/{listener_uuid}/health-check",
            json=req.to_dict(),
        )

    def delete_health_check(self, lb_uuid: str, listener_uuid: str) -> None:
        self._client.delete(f"/loadbalancer/{lb_uuid}/listeners/{listener_uuid}/health-check")
