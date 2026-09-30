from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

__all__ = [
    "Network",
    "CreateNetworkRequest",
    "UpdateNetworkRequest",
    "NetworkRoute",
    "CreateNetworkRouteRequest",
    "BGPPeer",
    "CreateBGPPeerRequest",
    "UpdateBGPPeerRequest",
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
        result = cls(**{k: data.get(k, f.default) for k, f in cls.__dataclass_fields__.items()})
        # The create endpoint answers with network_id and location
        if not result.id and "network_id" in data:
            result.id = data["network_id"]
        if not result.location_name and "location" in data:
            result.location_name = data["location"]
        return result


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
        result = cls(**{k: data.get(k, f.default) for k, f in cls.__dataclass_fields__.items()})
        # The create endpoint answers with route_id
        if not result.id and "route_id" in data:
            result.id = data["route_id"]
        return result


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


@dataclass
class BGPPeer:
    id: str = ""
    network_id: int = 0
    peer_type: str = ""
    """ip, vps or baremetal."""
    peer_target: str = ""
    remote_asn: int = 0
    max_prefix: int = 0
    description: str | None = None
    enabled: bool = True
    created_at: str = ""
    resolved_peer_ip: str | None = None
    """Neighbor IP resolved from the target; None while it cannot be resolved."""
    last_state: str | None = None
    """Session state seen by the network (Established, Active, Idle...)."""
    prefixes_received: int | None = None
    last_state_at: str | None = None
    received_prefixes: list[str] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> BGPPeer:
        result = cls(
            **{
                k: data.get(k, f.default_factory() if callable(f.default_factory) else f.default)
                for k, f in cls.__dataclass_fields__.items()
            }
        )
        # The create endpoint answers with peer_id
        if not result.id and "peer_id" in data:
            result.id = data["peer_id"]
        return result


@dataclass
class CreateBGPPeerRequest:
    peer_type: str
    """ip, vps or baremetal."""
    peer_target: str
    """An IP of the network, or the id of a VPS or baremetal attached to it."""
    remote_asn: int
    max_prefix: int = 100
    description: str | None = None

    def to_dict(self) -> dict[str, Any]:
        d: dict[str, Any] = {
            "peer_type": self.peer_type,
            "peer_target": self.peer_target,
            "remote_asn": self.remote_asn,
            "max_prefix": self.max_prefix,
        }
        if self.description is not None:
            d["description"] = self.description
        return d


@dataclass
class UpdateBGPPeerRequest:
    max_prefix: int | None = None
    description: str | None = None
    enabled: bool | None = None

    def to_dict(self) -> dict[str, Any]:
        d: dict[str, Any] = {}
        if self.max_prefix is not None:
            d["max_prefix"] = self.max_prefix
        if self.description is not None:
            d["description"] = self.description
        if self.enabled is not None:
            d["enabled"] = self.enabled
        return d
