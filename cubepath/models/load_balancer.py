from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

__all__ = [
    "LoadBalancer", "LBPlan", "LBFloatingIP", "LBListener", "LBTarget",
    "LBLocationPlans", "HealthCheckConfig",
    "CreateLoadBalancerRequest", "UpdateLoadBalancerRequest",
    "CreateListenerRequest", "UpdateListenerRequest",
    "AddTargetRequest", "UpdateTargetRequest",
]


@dataclass
class LBFloatingIP:
    address: str = ""
    type: str = ""

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> LBFloatingIP:
        return cls(**{k: data.get(k, v) for k, v in cls.__dataclass_fields__.items()})


@dataclass
class HealthCheckConfig:
    protocol: str = ""
    path: str = ""
    interval_seconds: int = 0
    timeout_seconds: int = 0
    healthy_threshold: int = 0
    unhealthy_threshold: int = 0
    expected_codes: str = ""

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> HealthCheckConfig:
        return cls(**{k: data.get(k, v) for k, v in cls.__dataclass_fields__.items()})

    def to_dict(self) -> dict[str, Any]:
        return {
            "protocol": self.protocol,
            "path": self.path,
            "interval_seconds": self.interval_seconds,
            "timeout_seconds": self.timeout_seconds,
            "healthy_threshold": self.healthy_threshold,
            "unhealthy_threshold": self.unhealthy_threshold,
            "expected_codes": self.expected_codes,
        }


@dataclass
class LBTarget:
    uuid: str = ""
    target_type: str = ""
    target_uuid: str = ""
    target_name: str = ""
    target_ip: str = ""
    port: int = 0
    weight: int = 0
    enabled: bool = True
    health_status: str = ""

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> LBTarget:
        return cls(**{k: data.get(k, v) for k, v in cls.__dataclass_fields__.items()})


@dataclass
class LBListener:
    uuid: str = ""
    name: str = ""
    protocol: str = ""
    source_port: int = 0
    target_port: int = 0
    algorithm: str = ""
    sticky_sessions: bool = False
    enabled: bool = True
    targets: list[LBTarget] = field(default_factory=list)
    targets_count: int = 0
    health_check: Any = None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> LBListener:
        hc_raw = data.get("health_check")
        hc = HealthCheckConfig.from_dict(hc_raw) if isinstance(hc_raw, dict) else hc_raw
        return cls(
            uuid=data.get("uuid", ""),
            name=data.get("name", ""),
            protocol=data.get("protocol", ""),
            source_port=data.get("source_port", 0),
            target_port=data.get("target_port", 0),
            algorithm=data.get("algorithm", ""),
            sticky_sessions=data.get("sticky_sessions", False),
            enabled=data.get("enabled", True),
            targets=[LBTarget.from_dict(t) for t in data.get("targets", [])],
            targets_count=data.get("targets_count", 0),
            health_check=hc,
        )


@dataclass
class LoadBalancer:
    uuid: str = ""
    name: str = ""
    label: str = ""
    status: str = ""
    location_name: str = ""
    plan: Any = None
    plan_name: str = ""
    floating_ips: list[LBFloatingIP] = field(default_factory=list)
    listeners: list[LBListener] = field(default_factory=list)
    listeners_count: int = 0
    project_id: str = ""
    created_at: str = ""

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> LoadBalancer:
        return cls(
            uuid=data.get("uuid", ""),
            name=data.get("name", ""),
            label=data.get("label", ""),
            status=data.get("status", ""),
            location_name=data.get("location_name", ""),
            plan=data.get("plan"),
            plan_name=data.get("plan_name", ""),
            floating_ips=[LBFloatingIP.from_dict(ip) for ip in data.get("floating_ips", [])],
            listeners=[LBListener.from_dict(li) for li in data.get("listeners", [])],
            listeners_count=data.get("listeners_count", 0),
            project_id=data.get("project_id", ""),
            created_at=data.get("created_at", ""),
        )


@dataclass
class LBPlan:
    name: str = ""
    price_per_hour: str = ""
    price_per_month: str = ""
    max_listeners: int = 0
    max_targets: int = 0
    connections_per_second: int = 0

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> LBPlan:
        return cls(**{k: data.get(k, v) for k, v in cls.__dataclass_fields__.items()})


@dataclass
class LBLocationPlans:
    location_name: str = ""
    location_description: str = ""
    plans: list[LBPlan] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> LBLocationPlans:
        return cls(
            location_name=data.get("location_name", ""),
            location_description=data.get("location_description", ""),
            plans=[LBPlan.from_dict(p) for p in data.get("plans", [])],
        )


# ── Requests ─────────────────────────────────────────────────────


@dataclass
class CreateLoadBalancerRequest:
    name: str
    plan_name: str
    location_name: str
    project_id: str = ""
    label: str = ""

    def to_dict(self) -> dict[str, Any]:
        d: dict[str, Any] = {
            "name": self.name,
            "plan_name": self.plan_name,
            "location_name": self.location_name,
        }
        if self.project_id:
            d["project_id"] = self.project_id
        if self.label:
            d["label"] = self.label
        return d


@dataclass
class UpdateLoadBalancerRequest:
    name: str = ""
    label: str = ""

    def to_dict(self) -> dict[str, Any]:
        d: dict[str, Any] = {}
        if self.name:
            d["name"] = self.name
        if self.label:
            d["label"] = self.label
        return d


@dataclass
class CreateListenerRequest:
    name: str
    protocol: str
    source_port: int
    target_port: int
    algorithm: str
    sticky_sessions: bool = False

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "protocol": self.protocol,
            "source_port": self.source_port,
            "target_port": self.target_port,
            "algorithm": self.algorithm,
            "sticky_sessions": self.sticky_sessions,
        }


@dataclass
class UpdateListenerRequest:
    name: str = ""
    target_port: int | None = None
    algorithm: str = ""
    enabled: bool | None = None

    def to_dict(self) -> dict[str, Any]:
        d: dict[str, Any] = {}
        if self.name:
            d["name"] = self.name
        if self.target_port is not None:
            d["target_port"] = self.target_port
        if self.algorithm:
            d["algorithm"] = self.algorithm
        if self.enabled is not None:
            d["enabled"] = self.enabled
        return d


@dataclass
class AddTargetRequest:
    target_type: str
    target_uuid: str
    weight: int
    port: int | None = None

    def to_dict(self) -> dict[str, Any]:
        d: dict[str, Any] = {
            "target_type": self.target_type,
            "target_uuid": self.target_uuid,
            "weight": self.weight,
        }
        if self.port is not None:
            d["port"] = self.port
        return d


@dataclass
class UpdateTargetRequest:
    port: int | None = None
    weight: int | None = None
    enabled: bool | None = None

    def to_dict(self) -> dict[str, Any]:
        d: dict[str, Any] = {}
        if self.port is not None:
            d["port"] = self.port
        if self.weight is not None:
            d["weight"] = self.weight
        if self.enabled is not None:
            d["enabled"] = self.enabled
        return d
