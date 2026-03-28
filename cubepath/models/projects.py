from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

__all__ = ["Project", "ProjectResponse", "CreateProjectRequest"]


@dataclass
class Project:
    id: str = ""
    name: str = ""
    description: str = ""
    created_at: str = ""

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Project:
        return cls(
            id=data.get("id", ""),
            name=data.get("name", ""),
            description=data.get("description", ""),
            created_at=data.get("created_at", ""),
        )


@dataclass
class ProjectResponse:
    project: Project = field(default_factory=Project)
    vps: list[Any] = field(default_factory=list)
    networks: list[Any] = field(default_factory=list)
    baremetals: list[Any] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> ProjectResponse:
        return cls(
            project=Project.from_dict(data.get("project", {})),
            vps=data.get("vps", []),
            networks=data.get("networks", []),
            baremetals=data.get("baremetals", []),
        )


@dataclass
class CreateProjectRequest:
    name: str
    description: str = ""

    def to_dict(self) -> dict[str, Any]:
        d: dict[str, Any] = {"name": self.name}
        if self.description:
            d["description"] = self.description
        return d
