from __future__ import annotations

from typing import TYPE_CHECKING, Any

from cubepath.models.cdn import (
    CDNMetricsParams,
    CDNOrigin,
    CDNPlan,
    CDNPurge,
    CDNPurgeStatus,
    CDNRule,
    CDNSignedURL,
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

    def get_metrics_summary(self, zone_uuid: str, params: CDNMetricsParams | None = None) -> Any:
        """Totals: requests, bandwidth, cache hit rate and error rate."""
        return self.get_metrics(zone_uuid, "summary", params)

    def get_metrics_requests(self, zone_uuid: str, params: CDNMetricsParams | None = None) -> Any:
        """Requests over time."""
        return self.get_metrics(zone_uuid, "requests", params)

    def get_metrics_bandwidth(self, zone_uuid: str, params: CDNMetricsParams | None = None) -> Any:
        """Bandwidth over time, or by region with group_by="region"."""
        return self.get_metrics(zone_uuid, "bandwidth", params)

    def get_metrics_cache(self, zone_uuid: str, params: CDNMetricsParams | None = None) -> Any:
        """Cache hits and misses over time."""
        return self.get_metrics(zone_uuid, "cache", params)

    def get_metrics_status_codes(self, zone_uuid: str, params: CDNMetricsParams | None = None) -> Any:
        """Requests by HTTP status code."""
        return self.get_metrics(zone_uuid, "status-codes", params)

    def get_metrics_top_urls(self, zone_uuid: str, params: CDNMetricsParams | None = None) -> Any:
        """Most requested URLs."""
        return self.get_metrics(zone_uuid, "top-urls", params)

    def get_metrics_top_countries(self, zone_uuid: str, params: CDNMetricsParams | None = None) -> Any:
        """Countries sending the most requests."""
        return self.get_metrics(zone_uuid, "top-countries", params)

    def get_metrics_top_asn(self, zone_uuid: str, params: CDNMetricsParams | None = None) -> Any:
        """Networks (ASN) sending the most requests."""
        return self.get_metrics(zone_uuid, "top-asn", params)

    def get_metrics_top_user_agents(self, zone_uuid: str, params: CDNMetricsParams | None = None) -> Any:
        """Most common user agents."""
        return self.get_metrics(zone_uuid, "top-user-agents", params)

    def get_metrics_blocked(self, zone_uuid: str, params: CDNMetricsParams | None = None) -> Any:
        """Requests blocked by WAF and rate limit rules."""
        return self.get_metrics(zone_uuid, "blocked", params)

    def get_metrics_pops(self, zone_uuid: str, params: CDNMetricsParams | None = None) -> Any:
        """Requests by CDN location."""
        return self.get_metrics(zone_uuid, "pops", params)

    def get_metrics_file_extensions(self, zone_uuid: str, params: CDNMetricsParams | None = None) -> Any:
        """Requests by file extension."""
        return self.get_metrics(zone_uuid, "file-extensions", params)

    # ── Actions ──────────────────────────────────────────────────

    def request_ssl(self, zone_uuid: str) -> Any:
        """Re-trigger automatic SSL issuance for the zone's current custom_domain.

        Use after fixing a missing/incorrect CNAME — the PATCH zone flow only
        queues a cert task when custom_domain changes, so this is the way to
        retry without resetting the field.
        """
        return self._client.post(f"/cdn/zones/{zone_uuid}/request-ssl")

    def move_zone_to_project(self, zone_uuid: str, project_id: int) -> Any:
        """Reassign a CDN zone to a different project in the same organization."""
        return self._client.post(
            f"/cdn/zones/{zone_uuid}/move-project",
            json={"project_id": project_id},
        )

    # ── Cache purge ──────────────────────────────────────────────

    def purge_cache(self, zone_uuid: str, *, everything: bool = False, paths: list[str] | None = None) -> CDNPurge:
        """Purge every cached file, or up to 100 paths (a trailing * purges a prefix). Set exactly one."""
        data: dict[str, Any] = self._client.post(
            f"/cdn/zones/{zone_uuid}/purge-cache",
            json={"everything": everything, "paths": paths or []},
        )
        return CDNPurge.from_dict(data)

    def list_purges(self, zone_uuid: str) -> list[CDNPurgeStatus]:
        """Latest 20 purges of the zone, newest first, with their progress per CDN location."""
        data: list[dict[str, Any]] = self._client.get(f"/cdn/zones/{zone_uuid}/purge-cache")
        return [CDNPurgeStatus.from_dict(p) for p in data]

    # ── Token Auth ───────────────────────────────────────────────

    def rotate_token_secret(self, zone_uuid: str) -> str:
        """Generate a new Token Auth secret and return it. It cannot be read again later."""
        data: dict[str, Any] = self._client.post(f"/cdn/zones/{zone_uuid}/token-auth/rotate-secret")
        secret: str = data.get("token_auth_secret", "")
        return secret

    def sign_url(
        self, zone_uuid: str, path: str, *, expires_in: int = 3600, client_ip: str | None = None
    ) -> CDNSignedURL:
        """Signed URL for a zone with Token Auth, valid expires_in seconds (60 to 604800).

        client_ip is required when the zone binds URLs to the client IP.
        """
        body: dict[str, Any] = {"path": path, "expires_in": expires_in}
        if client_ip is not None:
            body["client_ip"] = client_ip
        data: dict[str, Any] = self._client.post(f"/cdn/zones/{zone_uuid}/token-auth/sign-url", json=body)
        return CDNSignedURL.from_dict(data)
