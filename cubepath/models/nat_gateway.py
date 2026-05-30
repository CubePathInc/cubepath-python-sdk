from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Union

__all__ = [
    "NATGatewayPlan",
    "NATGatewayLocationPlans",
    "NATGatewayFloatingIP",
    "NATGateway",
    "CreateNATGatewayRequest",
    "UpdateNATGatewayRequest",
]


@dataclass
class NATGatewayPlan:
    name: str = ""
    description: str = ""
    price_per_hour: Union[str, float] = ""
    bandwidth_mbps: int = 0
    connections_per_second: int = 0

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> NATGatewayPlan:
        return cls(**{k: data.get(k, f.default) for k, f in cls.__dataclass_fields__.items()})


@dataclass
class NATGatewayLocationPlans:
    location_name: str = ""
    location_description: str = ""
    plans: list[NATGatewayPlan] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> NATGatewayLocationPlans:
        return cls(
            location_name=data.get("location_name", ""),
            location_description=data.get("location_description", ""),
            plans=[NATGatewayPlan.from_dict(p) for p in data.get("plans", [])],
        )


@dataclass
class NATGatewayFloatingIP:
    address: str = ""
    netmask: str = ""
    type: str = ""
    rdns: str = ""

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> NATGatewayFloatingIP:
        return cls(**{k: data.get(k, f.default) for k, f in cls.__dataclass_fields__.items()})


@dataclass
class NATGateway:
    uuid: str = ""
    name: str = ""
    label: str = ""
    status: str = ""
    plan_name: str = ""
    location_name: str = ""
    project_id: int = 0
    project_name: str = ""
    network_id: int = 0
    network_name: str = ""
    network_cidr: str = ""
    private_ip: str = ""
    monthly_charges: float = 0.0
    floating_ips: list[NATGatewayFloatingIP] = field(default_factory=list)
    protected: bool = False
    created_at: str = ""

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> NATGateway:
        return cls(
            uuid=data.get("uuid", ""),
            name=data.get("name", ""),
            label=data.get("label", ""),
            status=data.get("status", ""),
            plan_name=data.get("plan_name", ""),
            location_name=data.get("location_name", ""),
            project_id=data.get("project_id", 0),
            project_name=data.get("project_name", ""),
            network_id=data.get("network_id", 0),
            network_name=data.get("network_name", ""),
            network_cidr=data.get("network_cidr", ""),
            private_ip=data.get("private_ip", ""),
            monthly_charges=data.get("monthly_charges", 0.0),
            floating_ips=[NATGatewayFloatingIP.from_dict(ip) for ip in data.get("floating_ips", [])],
            protected=data.get("protected", False),
            created_at=data.get("created_at", ""),
        )


# ── Requests ─────────────────────────────────────────────────────


@dataclass
class CreateNATGatewayRequest:
    name: str
    plan_name: str
    network_id: int
    label: str = ""
    project_id: int | None = None

    def to_dict(self) -> dict[str, Any]:
        d: dict[str, Any] = {
            "name": self.name,
            "plan_name": self.plan_name,
            "network_id": self.network_id,
        }
        if self.label:
            d["label"] = self.label
        if self.project_id is not None:
            d["project_id"] = self.project_id
        return d


@dataclass
class UpdateNATGatewayRequest:
    name: str = ""
    label: str = ""

    def to_dict(self) -> dict[str, Any]:
        d: dict[str, Any] = {}
        if self.name:
            d["name"] = self.name
        if self.label:
            d["label"] = self.label
        return d
