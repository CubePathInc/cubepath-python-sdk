from __future__ import annotations

from dataclasses import dataclass
from typing import Any

__all__ = ["Network", "CreateNetworkRequest", "UpdateNetworkRequest"]


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
