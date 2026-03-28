from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

__all__ = ["FloatingIP", "FloatingIPsResponse", "Subnet"]


@dataclass
class FloatingIP:
    id: str = ""
    address: str = ""
    type: str = ""
    status: str = ""
    is_primary: bool = False
    location_name: str = ""
    protection_type: str = ""
    vps_name: str = ""
    baremetal_name: str = ""

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> FloatingIP:
        return cls(**{k: data.get(k, v) for k, v in cls.__dataclass_fields__.items()})


@dataclass
class Subnet:
    prefix: str = ""
    protection_type: str = ""
    ip_addresses: list[FloatingIP] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Subnet:
        return cls(
            prefix=data.get("prefix", ""),
            protection_type=data.get("protection_type", ""),
            ip_addresses=[FloatingIP.from_dict(ip) for ip in data.get("ip_addresses", [])],
        )


@dataclass
class FloatingIPsResponse:
    single_ips: list[FloatingIP] = field(default_factory=list)
    subnets: list[Subnet] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> FloatingIPsResponse:
        return cls(
            single_ips=[FloatingIP.from_dict(ip) for ip in data.get("single_ips", [])],
            subnets=[Subnet.from_dict(s) for s in data.get("subnets", [])],
        )
