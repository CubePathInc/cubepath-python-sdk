from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

__all__ = [
    "VPS",
    "VPSPlan",
    "VPSTemplate",
    "VPSAppTemplate",
    "VPSTemplatesResponse",
    "Location",
    "NetworkInfo",
    "TaskResponse",
    "CreateVPSRequest",
    "UpdateVPSRequest",
    "VPSBackup",
    "VPSBackupSettings",
    "CreateVPSBackupRequest",
    "UpdateVPSBackupSettingsRequest",
    "ISO",
    "ISOListResponse",
]


@dataclass
class VPSPlan:
    id: str = ""
    plan_name: str = ""
    cpu: int = 0
    ram: int = 0
    storage: int = 0
    bandwidth: int = 0
    price_per_hour: str = ""

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> VPSPlan:
        return cls(**{k: data.get(k, f.default) for k, f in cls.__dataclass_fields__.items()})


@dataclass
class VPSTemplate:
    id: str = ""
    template_name: str = ""
    os_name: str = ""
    version: str = ""

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> VPSTemplate:
        return cls(**{k: data.get(k, f.default) for k, f in cls.__dataclass_fields__.items()})


@dataclass
class VPSAppTemplate:
    app_name: str = ""
    version: str = ""
    recommended_plan: str = ""
    app_docs: str = ""
    app_wiki: str = ""
    license_type: str = ""
    description: str = ""

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> VPSAppTemplate:
        return cls(**{k: data.get(k, f.default) for k, f in cls.__dataclass_fields__.items()})


@dataclass
class VPSTemplatesResponse:
    operating_systems: list[VPSTemplate] = field(default_factory=list)
    applications: list[VPSAppTemplate] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> VPSTemplatesResponse:
        return cls(
            operating_systems=[VPSTemplate.from_dict(t) for t in data.get("operating_systems", [])],
            applications=[VPSAppTemplate.from_dict(a) for a in data.get("applications", [])],
        )


@dataclass
class Location:
    id: str = ""
    location_name: str = ""
    description: str = ""

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Location:
        return cls(**{k: data.get(k, f.default) for k, f in cls.__dataclass_fields__.items()})


@dataclass
class NetworkInfo:
    id: str = ""
    name: str = ""
    assigned_ip: str = ""

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> NetworkInfo:
        return cls(**{k: data.get(k, f.default) for k, f in cls.__dataclass_fields__.items()})


@dataclass
class TaskResponse:
    task_id: str = ""
    message: str = ""
    detail: str = ""

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> TaskResponse:
        return cls(**{k: data.get(k, f.default) for k, f in cls.__dataclass_fields__.items()})


@dataclass
class VPS:
    id: str = ""
    name: str = ""
    label: str = ""
    project_id: str = ""
    status: str = ""
    user: str = ""
    plan: VPSPlan | None = None
    template: VPSTemplate | None = None
    location: Location | None = None
    floating_ips: Any = None
    ipv4: str = ""
    ipv6: str = ""
    network: NetworkInfo | None = None
    ssh_keys: list[str] = field(default_factory=list)
    created_at: str = ""

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> VPS:
        return cls(
            id=data.get("id", ""),
            name=data.get("name", ""),
            label=data.get("label", ""),
            project_id=data.get("project_id", ""),
            status=data.get("status", ""),
            user=data.get("user", ""),
            plan=VPSPlan.from_dict(data["plan"]) if data.get("plan") else None,
            template=VPSTemplate.from_dict(data["template"]) if data.get("template") else None,
            location=Location.from_dict(data["location"]) if data.get("location") else None,
            floating_ips=data.get("floating_ips"),
            ipv4=data.get("ipv4", ""),
            ipv6=data.get("ipv6", ""),
            network=NetworkInfo.from_dict(data["network"]) if data.get("network") else None,
            ssh_keys=data.get("ssh_keys", []),
            created_at=data.get("created_at", ""),
        )


@dataclass
class CreateVPSRequest:
    name: str
    plan_name: str
    template_name: str
    location_name: str
    label: str = ""
    network_id: str = ""
    ssh_key_ids: list[int] = field(default_factory=list)
    user: str = ""
    password: str = ""
    ipv4: bool = False
    enable_backups: bool = False
    custom_cloudinit: str = ""
    firewall_group_ids: list[str] = field(default_factory=list)
    availability_group_uuid: str = ""

    def to_dict(self) -> dict[str, Any]:
        d: dict[str, Any] = {
            "name": self.name,
            "plan_name": self.plan_name,
            "template_name": self.template_name,
            "location_name": self.location_name,
        }
        if self.label:
            d["label"] = self.label
        if self.network_id:
            d["network_id"] = self.network_id
        if self.ssh_key_ids:
            d["ssh_key_ids"] = self.ssh_key_ids
        if self.user:
            d["user"] = self.user
        if self.password:
            d["password"] = self.password
        if self.ipv4:
            d["ipv4"] = self.ipv4
        if self.enable_backups:
            d["enable_backups"] = self.enable_backups
        if self.custom_cloudinit:
            d["custom_cloudinit"] = self.custom_cloudinit
        if self.firewall_group_ids:
            d["firewall_group_ids"] = self.firewall_group_ids
        if self.availability_group_uuid:
            d["availability_group_uuid"] = self.availability_group_uuid
        return d


@dataclass
class UpdateVPSRequest:
    name: str = ""
    label: str = ""

    def to_dict(self) -> dict[str, Any]:
        d: dict[str, Any] = {}
        if self.name:
            d["name"] = self.name
        if self.label:
            d["label"] = self.label
        return d


# ── Backups ──────────────────────────────────────────────────────


@dataclass
class VPSBackup:
    id: str = ""
    backup_type: str = ""
    status: str = ""
    progress: int = 0
    size_gb: float = 0.0
    notes: str = ""
    created_at: str = ""

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> VPSBackup:
        return cls(**{k: data.get(k, f.default) for k, f in cls.__dataclass_fields__.items()})


@dataclass
class VPSBackupSettings:
    enabled: bool = False
    schedule_hour: int = 0
    retention_days: int = 0
    max_backups: int = 0

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> VPSBackupSettings:
        return cls(**{k: data.get(k, f.default) for k, f in cls.__dataclass_fields__.items()})


@dataclass
class CreateVPSBackupRequest:
    notes: str = ""

    def to_dict(self) -> dict[str, Any]:
        d: dict[str, Any] = {}
        if self.notes:
            d["notes"] = self.notes
        return d


@dataclass
class UpdateVPSBackupSettingsRequest:
    enabled: bool = False
    schedule_hour: int = 0
    retention_days: int = 0
    max_backups: int = 0

    def to_dict(self) -> dict[str, Any]:
        return {
            "enabled": self.enabled,
            "schedule_hour": self.schedule_hour,
            "retention_days": self.retention_days,
            "max_backups": self.max_backups,
        }


# ── ISOs ─────────────────────────────────────────────────────────


@dataclass
class ISO:
    id: str = ""
    name: str = ""
    file_size: int = 0
    is_mounted: bool = False

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> ISO:
        return cls(**{k: data.get(k, f.default) for k, f in cls.__dataclass_fields__.items()})


@dataclass
class ISOListResponse:
    items: list[ISO] = field(default_factory=list)
    mounted_iso_id: str = ""

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> ISOListResponse:
        return cls(
            items=[ISO.from_dict(i) for i in data.get("items", [])],
            mounted_iso_id=data.get("mounted_iso_id", ""),
        )
