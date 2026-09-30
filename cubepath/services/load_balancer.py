from __future__ import annotations

import builtins
from typing import TYPE_CHECKING, Any

from cubepath.exceptions import APIError
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
        """The API has no single-item endpoint, so the balancer is looked up in the list."""
        for lb in self.list():
            if lb.uuid == lb_uuid:
                return lb
        raise APIError(404, "Not Found", f"load balancer {lb_uuid} not found")

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

    def configure_protection(self, lb_uuid: str, enabled: bool) -> None:
        """A protected load balancer cannot be deleted."""
        self._client.post(f"/loadbalancer/{lb_uuid}/protection", json={"enabled": enabled})

    def move_to_project(self, lb_uuid: str, project_id: int) -> None:
        self._client.post(f"/loadbalancer/{lb_uuid}/move-project", json={"project_id": project_id})

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

    def add_targets(
        self, lb_uuid: str, listener_uuid: str, targets: builtins.list[AddTargetRequest]
    ) -> builtins.list[LBTarget]:
        """Add up to 50 targets in one call, all or nothing."""
        data: dict[str, Any] = self._client.post(
            f"/loadbalancer/{lb_uuid}/listeners/{listener_uuid}/targets/batch",
            json={"targets": [t.to_dict() for t in targets]},
        )
        return [LBTarget.from_dict(t) for t in data.get("targets", [])]

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
