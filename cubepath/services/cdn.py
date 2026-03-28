from __future__ import annotations

from typing import TYPE_CHECKING, Any

from cubepath.models.cdn import (
    CDNMetricsParams,
    CDNOrigin,
    CDNPlan,
    CDNRule,
    CDNZone,
    CreateCDNOriginRequest,
    CreateCDNRuleRequest,
    CreateCDNZoneRequest,
    UpdateCDNOriginRequest,
    UpdateCDNRuleRequest,
    UpdateCDNZoneRequest,
)

if TYPE_CHECKING:
    from cubepath.client import CubePathClient


class CDNService:
    def __init__(self, client: CubePathClient) -> None:
        self._client = client

    # ── Zones ────────────────────────────────────────────────────

    def list_zones(self) -> list[CDNZone]:
        data: list[dict[str, Any]] = self._client.get("/cdn/zones")
        return [CDNZone.from_dict(z) for z in data]

    def get_zone(self, zone_uuid: str) -> CDNZone:
        data: dict[str, Any] = self._client.get(f"/cdn/zones/{zone_uuid}")
        return CDNZone.from_dict(data)

    def create_zone(self, req: CreateCDNZoneRequest) -> CDNZone:
        data: dict[str, Any] = self._client.post("/cdn/zones", json=req.to_dict())
        return CDNZone.from_dict(data)

    def update_zone(self, zone_uuid: str, req: UpdateCDNZoneRequest) -> CDNZone:
        data: dict[str, Any] = self._client.patch(f"/cdn/zones/{zone_uuid}", json=req.to_dict())
        return CDNZone.from_dict(data)

    def delete_zone(self, zone_uuid: str) -> None:
        self._client.delete(f"/cdn/zones/{zone_uuid}")

    def get_zone_pricing(self, zone_uuid: str) -> Any:
        return self._client.get(f"/cdn/zones/{zone_uuid}/pricing")

    def list_plans(self) -> list[CDNPlan]:
        data: list[dict[str, Any]] = self._client.get("/cdn/plans")
        return [CDNPlan.from_dict(p) for p in data]

    # ── Origins ──────────────────────────────────────────────────

    def list_origins(self, zone_uuid: str) -> list[CDNOrigin]:
        data: list[dict[str, Any]] = self._client.get(f"/cdn/zones/{zone_uuid}/origins")
        return [CDNOrigin.from_dict(o) for o in data]

    def create_origin(self, zone_uuid: str, req: CreateCDNOriginRequest) -> CDNOrigin:
        data: dict[str, Any] = self._client.post(f"/cdn/zones/{zone_uuid}/origins", json=req.to_dict())
        return CDNOrigin.from_dict(data)

    def update_origin(self, zone_uuid: str, origin_uuid: str, req: UpdateCDNOriginRequest) -> CDNOrigin:
        data: dict[str, Any] = self._client.patch(
            f"/cdn/zones/{zone_uuid}/origins/{origin_uuid}",
            json=req.to_dict(),
        )
        return CDNOrigin.from_dict(data)

    def delete_origin(self, zone_uuid: str, origin_uuid: str) -> None:
        self._client.delete(f"/cdn/zones/{zone_uuid}/origins/{origin_uuid}")

    # ── Rules ────────────────────────────────────────────────────

    def list_rules(self, zone_uuid: str) -> list[CDNRule]:
        data: list[dict[str, Any]] = self._client.get(f"/cdn/zones/{zone_uuid}/rules")
        return [CDNRule.from_dict(r) for r in data]

    def get_rule(self, zone_uuid: str, rule_uuid: str) -> CDNRule:
        data: dict[str, Any] = self._client.get(f"/cdn/zones/{zone_uuid}/rules/{rule_uuid}")
        return CDNRule.from_dict(data)

    def create_rule(self, zone_uuid: str, req: CreateCDNRuleRequest) -> CDNRule:
        data: dict[str, Any] = self._client.post(f"/cdn/zones/{zone_uuid}/rules", json=req.to_dict())
        return CDNRule.from_dict(data)

    def update_rule(self, zone_uuid: str, rule_uuid: str, req: UpdateCDNRuleRequest) -> CDNRule:
        data: dict[str, Any] = self._client.patch(
            f"/cdn/zones/{zone_uuid}/rules/{rule_uuid}",
            json=req.to_dict(),
        )
        return CDNRule.from_dict(data)

    def delete_rule(self, zone_uuid: str, rule_uuid: str) -> None:
        self._client.delete(f"/cdn/zones/{zone_uuid}/rules/{rule_uuid}")

    # ── WAF Rules ────────────────────────────────────────────────

    def list_waf_rules(self, zone_uuid: str) -> list[CDNRule]:
        data: list[dict[str, Any]] = self._client.get(f"/cdn/zones/{zone_uuid}/waf-rules")
        return [CDNRule.from_dict(r) for r in data]

    def get_waf_rule(self, zone_uuid: str, rule_uuid: str) -> CDNRule:
        data: dict[str, Any] = self._client.get(f"/cdn/zones/{zone_uuid}/waf-rules/{rule_uuid}")
        return CDNRule.from_dict(data)

    def create_waf_rule(self, zone_uuid: str, req: CreateCDNRuleRequest) -> CDNRule:
        data: dict[str, Any] = self._client.post(f"/cdn/zones/{zone_uuid}/waf-rules", json=req.to_dict())
        return CDNRule.from_dict(data)

    def update_waf_rule(self, zone_uuid: str, rule_uuid: str, req: UpdateCDNRuleRequest) -> CDNRule:
        data: dict[str, Any] = self._client.patch(
            f"/cdn/zones/{zone_uuid}/waf-rules/{rule_uuid}",
            json=req.to_dict(),
        )
        return CDNRule.from_dict(data)

    def delete_waf_rule(self, zone_uuid: str, rule_uuid: str) -> None:
        self._client.delete(f"/cdn/zones/{zone_uuid}/waf-rules/{rule_uuid}")

    # ── Metrics ──────────────────────────────────────────────────

    def get_metrics(self, zone_uuid: str, metric_type: str, params: CDNMetricsParams | None = None) -> Any:
        return self._client.get(
            f"/cdn/zones/{zone_uuid}/metrics/{metric_type}",
            params=params.to_params() if params else None,
        )
