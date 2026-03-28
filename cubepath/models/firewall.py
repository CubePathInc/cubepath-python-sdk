from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

__all__ = [
    "FirewallGroup", "FirewallRule",
    "CreateFirewallGroupRequest", "UpdateFirewallGroupRequest",
    "VPSFirewallGroupsRequest", "VPSFirewallGroupsResponse",
]


@dataclass
class FirewallRule:
    direction: str = ""
    protocol: str = ""
    port: str = ""
    source: str = ""
    comment: str = ""

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> FirewallRule:
        return cls(**{k: data.get(k, v) for k, v in cls.__dataclass_fields__.items()})

    def to_dict(self) -> dict[str, Any]:
        d: dict[str, Any] = {"direction": self.direction, "protocol": self.protocol}
        if self.port:
            d["port"] = self.port
        if self.source:
            d["source"] = self.source
        if self.comment:
            d["comment"] = self.comment
        return d


@dataclass
class FirewallGroup:
    id: str = ""
    project_id: str = ""
    name: str = ""
    rules: list[FirewallRule] = field(default_factory=list)
    enabled: bool = False
    vps_count: int = 0

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> FirewallGroup:
        return cls(
            id=data.get("id", ""),
            project_id=data.get("project_id", ""),
            name=data.get("name", ""),
            rules=[FirewallRule.from_dict(r) for r in data.get("rules", [])],
            enabled=data.get("enabled", False),
            vps_count=data.get("vps_count", 0),
        )


@dataclass
class CreateFirewallGroupRequest:
    name: str
    rules: list[FirewallRule] = field(default_factory=list)
    enabled: bool = True

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "rules": [r.to_dict() for r in self.rules],
            "enabled": self.enabled,
        }


@dataclass
class UpdateFirewallGroupRequest:
    name: str = ""
    rules: list[FirewallRule] | None = None
    enabled: bool | None = None

    def to_dict(self) -> dict[str, Any]:
        d: dict[str, Any] = {}
        if self.name:
            d["name"] = self.name
        if self.rules is not None:
            d["rules"] = [r.to_dict() for r in self.rules]
        if self.enabled is not None:
            d["enabled"] = self.enabled
        return d


@dataclass
class VPSFirewallGroupsRequest:
    firewall_group_ids: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {"firewall_group_ids": self.firewall_group_ids}


@dataclass
class VPSFirewallGroupsResponse:
    message: str = ""
    vps_id: str = ""
    firewall_groups: list[Any] = field(default_factory=list)
    sync_task_created: bool = False

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> VPSFirewallGroupsResponse:
        return cls(**{k: data.get(k, v) for k, v in cls.__dataclass_fields__.items()})
