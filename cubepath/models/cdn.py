from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

__all__ = [
    "CDNZone", "CDNOrigin", "CDNRule", "CDNPlan", "CDNMetricsParams",
    "CreateCDNZoneRequest", "UpdateCDNZoneRequest",
    "CreateCDNOriginRequest", "UpdateCDNOriginRequest",
    "CreateCDNRuleRequest", "UpdateCDNRuleRequest",
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
    created_at: str = ""
    updated_at: str = ""

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> CDNOrigin:
        return cls(**{k: data.get(k, v) for k, v in cls.__dataclass_fields__.items()})


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
        return cls(**{k: data.get(k, v) for k, v in cls.__dataclass_fields__.items()})


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
        return cls(**{k: data.get(k, v) for k, v in cls.__dataclass_fields__.items()})


@dataclass
class CDNMetricsParams:
    minutes: int | None = None
    interval_seconds: int | None = None
    group_by: str = ""
    limit: int | None = None

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

    def to_dict(self) -> dict[str, Any]:
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
