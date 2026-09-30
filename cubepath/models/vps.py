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
    "VPSBackupList",
    "ISO",
    "ISOListResponse",
    "VPSConsole",
    "VPSPlanOption",
    "VPSClusterPlans",
    "VPSLocationPlans",
    "AvailabilityGroup",
    "AvailabilityGroupVPS",
    "CreateAvailabilityGroupRequest",
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
    ipv6: bool = True
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
        d["ipv6"] = self.ipv6
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
    vps_id: int = 0
    backup_type: str = ""
    status: str = ""
    progress: int = 0
    size_gb: float | None = None
    notes: str | None = None
    started_at: str | None = None
    completed_at: str | None = None
    error_message: str | None = None
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
class VPSBackupList:
    backups: list[VPSBackup] = field(default_factory=list)
    total: int = 0
    has_settings: bool = False
    settings: VPSBackupSettings | None = None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> VPSBackupList:
        return cls(
            backups=[VPSBackup.from_dict(b) for b in data.get("backups", [])],
            total=data.get("total", 0),
            has_settings=data.get("has_settings", False),
            settings=VPSBackupSettings.from_dict(data["settings"]) if data.get("settings") else None,
        )


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
    filename: str = ""
    file_size: int = 0
    description: str | None = None
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
            mounted_iso_id=data.get("mounted_iso_id") or "",
        )


# ── Console ──────────────────────────────────────────────────────


@dataclass
class VPSConsole:
    """noVNC connection: open websocket_url and authenticate with ticket."""

    websocket_url: str = ""
    session_id: str = ""
    ticket: str = ""

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> VPSConsole:
        return cls(
            websocket_url=data.get("websocket_url", ""),
            session_id=data.get("session_id", ""),
            ticket=(data.get("vnc_info") or {}).get("ticket", ""),
        )


# ── Plans ────────────────────────────────────────────────────────


@dataclass
class VPSPlanOption:
    plan_name: str = ""
    cpu: int = 0
    ram: int = 0
    """MB."""
    storage: int = 0
    """GB."""
    bandwidth: int = 0
    """TB per month."""
    price_per_hour: float = 0.0
    status: int = 0

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> VPSPlanOption:
        return cls(**{k: data.get(k, f.default) for k, f in cls.__dataclass_fields__.items()})


@dataclass
class VPSClusterPlans:
    cluster_name: str = ""
    type: str = ""
    plans: list[VPSPlanOption] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> VPSClusterPlans:
        return cls(
            cluster_name=data.get("cluster_name", ""),
            type=data.get("type", ""),
            plans=[VPSPlanOption.from_dict(p) for p in data.get("plans", [])],
        )


@dataclass
class VPSLocationPlans:
    location_name: str = ""
    description: str = ""
    clusters: list[VPSClusterPlans] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> VPSLocationPlans:
        return cls(
            location_name=data.get("location_name", ""),
            description=data.get("description", ""),
            clusters=[VPSClusterPlans.from_dict(c) for c in data.get("clusters", [])],
        )


# ── Availability groups ──────────────────────────────────────────


@dataclass
class AvailabilityGroupVPS:
    id: int = 0
    name: str = ""
    label: str = ""
    status: str = ""

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> AvailabilityGroupVPS:
        return cls(**{k: data.get(k, f.default) for k, f in cls.__dataclass_fields__.items()})


@dataclass
class AvailabilityGroup:
    uuid: str = ""
    project_id: int = 0
    name: str = ""
    description: str | None = None
    strategy: str = ""
    location_name: str = ""
    max_servers: int = 0
    vps_count: int = 0
    vps_list: list[AvailabilityGroupVPS] = field(default_factory=list)
    """Not returned on creation."""
    created_at: str = ""

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> AvailabilityGroup:
        return cls(
            uuid=data.get("uuid", ""),
            project_id=data.get("project_id", 0),
            name=data.get("name", ""),
            description=data.get("description"),
            strategy=data.get("strategy", ""),
            location_name=data.get("location_name", ""),
            max_servers=data.get("max_servers", 0),
            vps_count=data.get("vps_count", 0),
            vps_list=[AvailabilityGroupVPS.from_dict(v) for v in data.get("vps_list", [])],
            created_at=data.get("created_at", ""),
        )


@dataclass
class CreateAvailabilityGroupRequest:
    """A spread group: its servers run on different hosts."""

    project_id: int
    name: str
    location_name: str
    description: str | None = None

    def to_dict(self) -> dict[str, Any]:
        d: dict[str, Any] = {"project_id": self.project_id, "name": self.name, "location_name": self.location_name}
        if self.description is not None:
            d["description"] = self.description
        return d
