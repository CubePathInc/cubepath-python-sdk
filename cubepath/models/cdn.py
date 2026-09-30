from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

__all__ = [
    "CDNZone",
    "CDNOrigin",
    "CDNRule",
    "CDNPlan",
    "CDNMetricsParams",
    "CreateCDNZoneRequest",
    "UpdateCDNZoneRequest",
    "CreateCDNOriginRequest",
    "UpdateCDNOriginRequest",
    "CreateCDNRuleRequest",
    "UpdateCDNRuleRequest",
    "CDNPurge",
    "CDNPurgePop",
    "CDNPurgeStatus",
    "CDNSignedURL",
]


@dataclass
class CDNOrigin:
    uuid: str = ""
    name: str = ""
    address: str = ""
    port: int = 0
    protocol: str = ""
    weight: int = 0
    priority: int = 0
    is_backup: bool = False
    health_check_enabled: bool = False
    health_check_path: str = ""
    health_status: str = ""
    verify_ssl: bool = False
    host_header: str = ""
    base_path: str = ""
    enabled: bool = True
    object_storage_bucket_uuid: str | None = None
    """Set when the origin serves a CubePath Object Storage bucket."""
    created_at: str = ""
    updated_at: str = ""

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> CDNOrigin:
        return cls(**{k: data.get(k, f.default) for k, f in cls.__dataclass_fields__.items()})


@dataclass
class CDNRule:
    uuid: str = ""
    name: str = ""
    rule_type: str = ""
    priority: int = 0
    match_conditions: Any = None
    action_config: Any = None
    enabled: bool = True
    expires_at: str = ""
    created_at: str = ""
    updated_at: str = ""

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> CDNRule:
        return cls(**{k: data.get(k, f.default) for k, f in cls.__dataclass_fields__.items()})


@dataclass
class CDNZone:
    uuid: str = ""
    name: str = ""
    domain: str = ""
    custom_domain: str = ""
    status: str = ""
    plan_name: str = ""
    ssl_type: str = ""
    project_id: str = ""
    origins: list[CDNOrigin] = field(default_factory=list)
    rules: list[CDNRule] = field(default_factory=list)
    created_at: str = ""
    updated_at: str = ""
    token_auth_enabled: bool = False
    token_auth_ip_binding: bool = False
    token_auth_secret: str | None = None
    """Only returned by the update that first enabled Token Auth."""
    cors_enabled: bool = False
    cors_allow_origins: str | None = None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> CDNZone:
        return cls(
            uuid=data.get("uuid", ""),
            name=data.get("name", ""),
            domain=data.get("domain", ""),
            custom_domain=data.get("custom_domain", ""),
            status=data.get("status", ""),
            plan_name=data.get("plan_name", ""),
            ssl_type=data.get("ssl_type", ""),
            project_id=data.get("project_id", ""),
            origins=[CDNOrigin.from_dict(o) for o in data.get("origins", [])],
            rules=[CDNRule.from_dict(r) for r in data.get("rules", [])],
            created_at=data.get("created_at", ""),
            updated_at=data.get("updated_at", ""),
            token_auth_enabled=data.get("token_auth_enabled", False),
            token_auth_ip_binding=data.get("token_auth_ip_binding", False),
            token_auth_secret=data.get("token_auth_secret"),
            cors_enabled=data.get("cors_enabled", False),
            cors_allow_origins=data.get("cors_allow_origins"),
        )


@dataclass
class CDNPlan:
    uuid: str = ""
    name: str = ""
    description: str = ""
    price_per_gb: str = ""
    base_price_per_hour: str = ""
    max_zones: int = 0
    max_origins_per_zone: int = 0
    max_rules_per_zone: int = 0
    custom_ssl_allowed: bool = False

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> CDNPlan:
        return cls(**{k: data.get(k, f.default) for k, f in cls.__dataclass_fields__.items()})


@dataclass
class CDNMetricsParams:
    """Window and filters of the metrics endpoints; each endpoint ignores the ones it does not take."""

    minutes: int | None = None
    """Window looking back, default 60."""
    interval_seconds: int | None = None
    """Bucket size of the time series."""
    group_by: str = ""
    """bandwidth only: time (default) or region."""
    limit: int | None = None
    """top-* and file-extensions endpoints: number of rows, default 20."""
    country: str = ""
    asn: str = ""
    status_range: str = ""
    status: str = ""
    cache_status: str = ""
    device_type: str = ""
    path_prefix: str = ""

    def to_params(self) -> dict[str, Any]:
        d: dict[str, Any] = {}
        if self.minutes is not None:
            d["minutes"] = self.minutes
        if self.interval_seconds is not None:
            d["interval_seconds"] = self.interval_seconds
        if self.group_by:
            d["group_by"] = self.group_by
        if self.limit is not None:
            d["limit"] = self.limit
        for k in ("country", "asn", "status_range", "status", "cache_status", "device_type", "path_prefix"):
            v = getattr(self, k)
            if v:
                d[k] = v
        return d


# ── Requests ─────────────────────────────────────────────────────


@dataclass
class CreateCDNZoneRequest:
    name: str
    plan_name: str
    custom_domain: str = ""
    project_id: str = ""

    def to_dict(self) -> dict[str, Any]:
        d: dict[str, Any] = {"name": self.name, "plan_name": self.plan_name}
        if self.custom_domain:
            d["custom_domain"] = self.custom_domain
        if self.project_id:
            d["project_id"] = self.project_id
        return d


@dataclass
class UpdateCDNZoneRequest:
    name: str = ""
    custom_domain: str = ""
    ssl_type: str = ""
    certificate_uuid: str = ""
    token_auth_enabled: bool | None = None
    """Require signed URLs. The first activation generates the secret and returns it in the zone."""
    token_auth_ip_binding: bool | None = None
    """Bind signed URLs to the client IP."""
    cors_enabled: bool | None = None
    cors_allow_origins: str | None = None
    """"*" or a comma-separated list of origins."""

    def to_dict(self) -> dict[str, Any]:
        d: dict[str, Any] = {}
        if self.name:
            d["name"] = self.name
        if self.custom_domain:
            d["custom_domain"] = self.custom_domain
        if self.ssl_type:
            d["ssl_type"] = self.ssl_type
        if self.certificate_uuid:
            d["certificate_uuid"] = self.certificate_uuid
        for k in ("token_auth_enabled", "token_auth_ip_binding", "cors_enabled", "cors_allow_origins"):
            v = getattr(self, k)
            if v is not None:
                d[k] = v
        return d


@dataclass
class CreateCDNOriginRequest:
    name: str
    weight: int
    priority: int
    is_backup: bool = False
    health_check_enabled: bool = False
    health_check_path: str = ""
    verify_ssl: bool = False
    enabled: bool = True
    origin_url: str = ""
    address: str = ""
    port: int | None = None
    protocol: str = ""
    host_header: str = ""
    base_path: str = ""
    object_storage_bucket_uuid: str = ""
    """Serve a CubePath Object Storage bucket. The API then sets every connection field itself,
    so only name, weight, priority and is_backup are sent next to it."""

    def to_dict(self) -> dict[str, Any]:
        if self.object_storage_bucket_uuid:
            return {
                "name": self.name,
                "object_storage_bucket_uuid": self.object_storage_bucket_uuid,
                "weight": self.weight,
                "priority": self.priority,
                "is_backup": self.is_backup,
            }
        d: dict[str, Any] = {
            "name": self.name,
            "weight": self.weight,
            "priority": self.priority,
            "is_backup": self.is_backup,
            "health_check_enabled": self.health_check_enabled,
            "verify_ssl": self.verify_ssl,
            "enabled": self.enabled,
        }
        if self.origin_url:
            d["origin_url"] = self.origin_url
        if self.address:
            d["address"] = self.address
        if self.port is not None:
            d["port"] = self.port
        if self.protocol:
            d["protocol"] = self.protocol
        if self.health_check_path:
            d["health_check_path"] = self.health_check_path
        if self.host_header:
            d["host_header"] = self.host_header
        if self.base_path:
            d["base_path"] = self.base_path
        return d


@dataclass
class UpdateCDNOriginRequest:
    name: str = ""
    address: str = ""
    port: int | None = None
    protocol: str = ""
    weight: int | None = None
    priority: int | None = None
    host_header: str = ""
    base_path: str = ""
    health_check_enabled: bool | None = None
    health_check_path: str = ""
    verify_ssl: bool | None = None
    enabled: bool | None = None

    def to_dict(self) -> dict[str, Any]:
        d: dict[str, Any] = {}
        if self.name:
            d["name"] = self.name
        if self.address:
            d["address"] = self.address
        if self.port is not None:
            d["port"] = self.port
        if self.protocol:
            d["protocol"] = self.protocol
        if self.weight is not None:
            d["weight"] = self.weight
        if self.priority is not None:
            d["priority"] = self.priority
        if self.host_header:
            d["host_header"] = self.host_header
        if self.base_path:
            d["base_path"] = self.base_path
        if self.health_check_enabled is not None:
            d["health_check_enabled"] = self.health_check_enabled
        if self.health_check_path:
            d["health_check_path"] = self.health_check_path
        if self.verify_ssl is not None:
            d["verify_ssl"] = self.verify_ssl
        if self.enabled is not None:
            d["enabled"] = self.enabled
        return d


@dataclass
class CreateCDNRuleRequest:
    name: str
    rule_type: str
    priority: int
    action_config: Any
    match_conditions: Any = None
    enabled: bool = True

    def to_dict(self) -> dict[str, Any]:
        d: dict[str, Any] = {
            "name": self.name,
            "rule_type": self.rule_type,
            "priority": self.priority,
            "action_config": self.action_config,
            "enabled": self.enabled,
        }
        if self.match_conditions is not None:
            d["match_conditions"] = self.match_conditions
        return d


@dataclass
class UpdateCDNRuleRequest:
    name: str = ""
    priority: int | None = None
    match_conditions: Any = None
    action_config: Any = None
    enabled: bool | None = None

    def to_dict(self) -> dict[str, Any]:
        d: dict[str, Any] = {}
        if self.name:
            d["name"] = self.name
        if self.priority is not None:
            d["priority"] = self.priority
        if self.match_conditions is not None:
            d["match_conditions"] = self.match_conditions
        if self.action_config is not None:
            d["action_config"] = self.action_config
        if self.enabled is not None:
            d["enabled"] = self.enabled
        return d


# ── Cache purge and Token Auth ───────────────────────────────────


@dataclass
class CDNPurge:
    """A queued purge, or the equivalent one already running."""

    detail: str = ""
    purge_uuid: str = ""
    status: str = ""
    """pending, in_progress, completed, partial, failed or expired."""

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> CDNPurge:
        return cls(**{k: data.get(k, f.default) for k, f in cls.__dataclass_fields__.items()})


@dataclass
class CDNPurgePop:
    pop: str = ""
    expected: int = 0
    completed: int = 0
    failed: int = 0

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> CDNPurgePop:
        return cls(**{k: data.get(k, f.default) for k, f in cls.__dataclass_fields__.items()})


@dataclass
class CDNPurgeStatus:
    purge_uuid: str = ""
    scope: str = ""
    """everything or paths."""
    paths: list[str] = field(default_factory=list)
    status: str = ""
    requested_at: str | None = None
    completed_at: str | None = None
    nodes_expected: int = 0
    nodes_completed: int = 0
    nodes_failed: int = 0
    pops: list[CDNPurgePop] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> CDNPurgeStatus:
        nodes = data.get("nodes") or {}
        return cls(
            purge_uuid=data.get("purge_uuid", ""),
            scope=data.get("scope", ""),
            paths=data.get("paths") or [],
            status=data.get("status", ""),
            requested_at=data.get("requested_at"),
            completed_at=data.get("completed_at"),
            nodes_expected=nodes.get("expected", 0),
            nodes_completed=nodes.get("completed", 0),
            nodes_failed=nodes.get("failed", 0),
            pops=[CDNPurgePop.from_dict(p) for p in data.get("pops", [])],
        )


@dataclass
class CDNSignedURL:
    signed_url: str = ""
    token: str = ""
    expires: int = 0
    """Unix timestamp."""

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> CDNSignedURL:
        return cls(**{k: data.get(k, f.default) for k, f in cls.__dataclass_fields__.items()})
