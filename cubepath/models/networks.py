from __future__ import annotations

from dataclasses import dataclass
from typing import Any

__all__ = [
    "Network",
    "CreateNetworkRequest",
    "UpdateNetworkRequest",
    "NetworkRoute",
    "CreateNetworkRouteRequest",
]


@dataclass
class Network:
    id: str = ""
    name: str = ""
    label: str = ""
    project_id: str = ""
    location_name: str = ""
    ip_range: str = ""
    prefix: int = 0
    created_at: str = ""

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Network:
        return cls(**{k: data.get(k, f.default) for k, f in cls.__dataclass_fields__.items()})


@dataclass
class CreateNetworkRequest:
    name: str
    location_name: str
    ip_range: str
    prefix: int
    project_id: str
    label: str = ""

    def to_dict(self) -> dict[str, Any]:
        d: dict[str, Any] = {
            "name": self.name,
            "location_name": self.location_name,
            "ip_range": self.ip_range,
            "prefix": self.prefix,
            "project_id": self.project_id,
        }
        if self.label:
            d["label"] = self.label
        return d


@dataclass
class UpdateNetworkRequest:
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
class NetworkRoute:
    id: str = ""
    network_id: int = 0
    destination: str = ""
    next_hop_type: str = ""
    next_hop_target: str = ""
    resolved_next_hop_ip: str = ""
    description: str = ""
    created_at: str = ""
    nat_gateway_uuid: str = ""
    nat_gateway_name: str = ""

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> NetworkRoute:
        return cls(**{k: data.get(k, f.default) for k, f in cls.__dataclass_fields__.items()})


@dataclass
class CreateNetworkRouteRequest:
    destination: str
    next_hop_type: str
    next_hop_target: str
    description: str = ""

    def to_dict(self) -> dict[str, Any]:
        d: dict[str, Any] = {
            "destination": self.destination,
            "next_hop_type": self.next_hop_type,
            "next_hop_target": self.next_hop_target,
        }
        if self.description:
            d["description"] = self.description
        return d
