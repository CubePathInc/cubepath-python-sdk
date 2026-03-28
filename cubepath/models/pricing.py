from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

__all__ = [
    "PricingResponse",
    "VPSPricing",
    "LocationPricing",
    "PricingCluster",
    "BaremetalPricing",
    "BaremetalLocationPricing",
    "BaremetalModelPrice",
]


@dataclass
class PricingCluster:
    cluster_name: str = ""
    plans: list[Any] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> PricingCluster:
        return cls(
            cluster_name=data.get("cluster_name", ""),
            plans=data.get("plans", []),
        )


@dataclass
class LocationPricing:
    location_name: str = ""
    description: str = ""
    clusters: list[PricingCluster] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> LocationPricing:
        return cls(
            location_name=data.get("location_name", ""),
            description=data.get("description", ""),
            clusters=[PricingCluster.from_dict(c) for c in data.get("clusters", [])],
        )


@dataclass
class VPSPricing:
    locations: list[LocationPricing] = field(default_factory=list)
    templates: list[Any] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> VPSPricing:
        return cls(
            locations=[LocationPricing.from_dict(loc) for loc in data.get("locations", [])],
            templates=data.get("templates", []),
        )


@dataclass
class BaremetalModelPrice:
    model_name: str = ""
    cpu: str = ""
    cpu_specs: str = ""
    ram_size: str = ""
    ram_type: str = ""
    disk_size: str = ""
    disk_type: str = ""
    port: str = ""
    price: str = ""
    setup: str = ""
    stock_available: bool = False

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> BaremetalModelPrice:
        return cls(**{k: data.get(k, f.default) for k, f in cls.__dataclass_fields__.items()})


@dataclass
class BaremetalLocationPricing:
    location_name: str = ""
    description: str = ""
    baremetal_models: list[BaremetalModelPrice] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> BaremetalLocationPricing:
        return cls(
            location_name=data.get("location_name", ""),
            description=data.get("description", ""),
            baremetal_models=[BaremetalModelPrice.from_dict(m) for m in data.get("baremetal_models", [])],
        )


@dataclass
class BaremetalPricing:
    locations: list[BaremetalLocationPricing] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> BaremetalPricing:
        return cls(
            locations=[BaremetalLocationPricing.from_dict(loc) for loc in data.get("locations", [])],
        )


@dataclass
class PricingResponse:
    vps: VPSPricing | None = None
    baremetal: BaremetalPricing | None = None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> PricingResponse:
        return cls(
            vps=VPSPricing.from_dict(data["vps"]) if data.get("vps") else None,
            baremetal=BaremetalPricing.from_dict(data["baremetal"]) if data.get("baremetal") else None,
        )
