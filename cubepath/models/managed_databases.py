from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

__all__ = [
    "ManagedDatabasePlan",
    "ManagedDatabaseLocationPlans",
    "ManagedDatabaseLocation",
    "ManagedDatabase",
    "ManagedDatabaseDetail",
    "ManagedDatabaseBackupConfig",
    "ManagedDatabaseBackupPolicyUpdate",
    "CreateManagedDatabaseRequest",
    "CreateManagedDatabaseResponse",
    "UpdateManagedDatabaseRequest",
    "ManagedDatabaseScaleResponse",
    "ManagedDatabaseCredentials",
    "ManagedDatabaseConfigParam",
    "ManagedDatabaseConfig",
    "ManagedDatabaseConfigUpdateResponse",
    "ManagedDatabaseMetrics",
    "LogicalDatabase",
    "ManagedDatabaseUser",
    "CreateManagedDatabaseUserRequest",
    "CreateManagedDatabaseUserResponse",
]


def _simple(cls: Any, data: dict[str, Any] | None) -> Any:
    data = data or {}
    return cls(
        **{
            k: data.get(k, f.default_factory() if callable(f.default_factory) else f.default)
            for k, f in cls.__dataclass_fields__.items()
        }
    )


# ── Plans ────────────────────────────────────────────────────────


@dataclass
class ManagedDatabasePlan:
    uuid: str = ""
    name: str = ""
    description: str | None = None
    engine: str = ""
    cpu: int = 0
    """Per node."""
    memory_gb: int = 0
    """Per node."""
    storage_gb: int = 0
    """Per node."""
    max_replicas: int = 0
    price_per_hour: float = 0.0
    """Per node per hour: the database costs price_per_hour x replicas."""

    @classmethod
    def from_dict(cls, data: dict[str, Any] | None) -> ManagedDatabasePlan:
        result: ManagedDatabasePlan = _simple(cls, data)
        return result


@dataclass
class ManagedDatabaseLocationPlans:
    location_name: str = ""
    location_description: str | None = None
    plans: list[ManagedDatabasePlan] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> ManagedDatabaseLocationPlans:
        return cls(
            location_name=data.get("location_name", ""),
            location_description=data.get("location_description"),
            plans=[ManagedDatabasePlan.from_dict(p) for p in data.get("plans", [])],
        )


# ── Instances ────────────────────────────────────────────────────


@dataclass
class ManagedDatabaseLocation:
    id: int = 0
    location_name: str = ""
    description: str | None = None

    @classmethod
    def from_dict(cls, data: dict[str, Any] | None) -> ManagedDatabaseLocation:
        result: ManagedDatabaseLocation = _simple(cls, data)
        return result


@dataclass
class ManagedDatabase:
    uuid: str = ""
    project_id: int = 0
    name: str = ""
    label: str | None = None
    engine: str = ""
    """mysql, valkey or postgresql."""
    version: str = ""
    status: str = ""
    """provisioning, active, updating, scaling, backing_up, restoring, degraded, suspended, error or deleting."""
    endpoint_host: str | None = None
    """Public address; None until provisioned."""
    endpoint_port: int | None = None
    replicas: int = 0
    protected: bool = False

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> ManagedDatabase:
        result: ManagedDatabase = _simple(cls, data)
        return result


@dataclass
class ManagedDatabaseDetail(ManagedDatabase):
    topology: str = ""
    plan: ManagedDatabasePlan = field(default_factory=ManagedDatabasePlan)
    location: ManagedDatabaseLocation = field(default_factory=ManagedDatabaseLocation)
    backup_enabled: bool = False
    backup_schedule_cron: str | None = None
    backup_retention_days: int = 7
    billing_type: str = ""
    updated_at: str = ""

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> ManagedDatabaseDetail:
        result: ManagedDatabaseDetail = _simple(cls, data)
        result.plan = ManagedDatabasePlan.from_dict(data.get("plan"))
        result.location = ManagedDatabaseLocation.from_dict(data.get("location"))
        return result


@dataclass
class ManagedDatabaseBackupConfig:
    schedule_cron: str
    """5-field cron expression (minute hour day month weekday)."""
    retention_days: int = 7

    def to_dict(self) -> dict[str, Any]:
        return {"schedule_cron": self.schedule_cron, "retention_days": self.retention_days}


@dataclass
class ManagedDatabaseBackupPolicyUpdate:
    enabled: bool | None = None
    schedule_cron: str | None = None
    retention_days: int | None = None

    def to_dict(self) -> dict[str, Any]:
        d: dict[str, Any] = {}
        if self.enabled is not None:
            d["enabled"] = self.enabled
        if self.schedule_cron is not None:
            d["schedule_cron"] = self.schedule_cron
        if self.retention_days is not None:
            d["retention_days"] = self.retention_days
        return d


@dataclass
class CreateManagedDatabaseRequest:
    project_id: int
    name: str
    engine: str
    """mysql, valkey or postgresql."""
    version: str
    plan_uuid: str
    replicas: int | None = None
    """Default 3. At least 3 for mysql and 2 for valkey and postgresql, at most the plan's max_replicas."""
    topology: str | None = None
    """Defaults per engine: mgr for mysql, replication for valkey and postgresql."""
    backup: ManagedDatabaseBackupConfig | None = None

    def to_dict(self) -> dict[str, Any]:
        d: dict[str, Any] = {
            "project_id": self.project_id,
            "name": self.name,
            "engine": self.engine,
            "version": self.version,
            "plan_uuid": self.plan_uuid,
        }
        if self.replicas is not None:
            d["replicas"] = self.replicas
        if self.topology is not None:
            d["topology"] = self.topology
        if self.backup is not None:
            d["backup"] = self.backup.to_dict()
        return d


@dataclass
class CreateManagedDatabaseResponse:
    detail: str = ""
    uuid: str = ""
    name: str = ""
    engine: str = ""
    version: str = ""
    status: str = ""

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> CreateManagedDatabaseResponse:
        result: CreateManagedDatabaseResponse = _simple(cls, data)
        return result


@dataclass
class UpdateManagedDatabaseRequest:
    name: str | None = None
    label: str | None = None
    backup: ManagedDatabaseBackupPolicyUpdate | None = None

    def to_dict(self) -> dict[str, Any]:
        d: dict[str, Any] = {}
        if self.name is not None:
            d["name"] = self.name
        if self.label is not None:
            d["label"] = self.label
        if self.backup is not None:
            d["backup"] = self.backup.to_dict()
        return d


@dataclass
class ManagedDatabaseScaleResponse:
    detail: str = ""
    uuid: str = ""
    replicas: int | None = None
    """Set for horizontal scaling."""
    plan: str | None = None
    """Set for vertical scaling."""

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> ManagedDatabaseScaleResponse:
        result: ManagedDatabaseScaleResponse = _simple(cls, data)
        return result


@dataclass
class ManagedDatabaseCredentials:
    host: str = ""
    port: int = 0
    username: str = ""
    password: str = ""
    uri: str = ""

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> ManagedDatabaseCredentials:
        result: ManagedDatabaseCredentials = _simple(cls, data)
        return result


@dataclass
class ManagedDatabaseConfigParam:
    type: str = ""
    default: int | float | str | None = None
    value: int | float | str | None = None
    value_source: str = ""
    requires_restart: bool = False
    description: str = ""
    min: int | float | str | None = None
    max: int | float | str | None = None
    enum: list[int | float | str] | None = None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> ManagedDatabaseConfigParam:
        result: ManagedDatabaseConfigParam = _simple(cls, data)
        return result


@dataclass
class ManagedDatabaseConfig:
    engine: str = ""
    params: dict[str, ManagedDatabaseConfigParam] = field(default_factory=dict)
    note: str = ""

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> ManagedDatabaseConfig:
        return cls(
            engine=data.get("engine", ""),
            params={k: ManagedDatabaseConfigParam.from_dict(v) for k, v in (data.get("params") or {}).items()},
            note=data.get("note", ""),
        )


@dataclass
class ManagedDatabaseConfigUpdateResponse:
    detail: str = ""
    uuid: str = ""
    requires_restart: list[str] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> ManagedDatabaseConfigUpdateResponse:
        result: ManagedDatabaseConfigUpdateResponse = _simple(cls, data)
        return result


@dataclass
class ManagedDatabaseMetrics:
    start: int = 0
    end: int = 0
    metrics: dict[str, list[list[float]]] = field(default_factory=dict)
    """Series name to [unix_timestamp, value] points."""

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> ManagedDatabaseMetrics:
        result: ManagedDatabaseMetrics = _simple(cls, data)
        return result


# ── Logical databases and users ──────────────────────────────────


@dataclass
class LogicalDatabase:
    uuid: str = ""
    name: str = ""
    status: str = ""
    created_at: str | None = None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> LogicalDatabase:
        result: LogicalDatabase = _simple(cls, data)
        return result


@dataclass
class ManagedDatabaseUser:
    uuid: str = ""
    username: str = ""
    status: str = ""
    created_at: str | None = None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> ManagedDatabaseUser:
        result: ManagedDatabaseUser = _simple(cls, data)
        return result


@dataclass
class CreateManagedDatabaseUserRequest:
    username: str
    password: str | None = None
    """12-64 characters; a secure one is generated when omitted."""

    def to_dict(self) -> dict[str, Any]:
        d: dict[str, Any] = {"username": self.username}
        if self.password is not None:
            d["password"] = self.password
        return d


@dataclass
class CreateManagedDatabaseUserResponse:
    detail: str = ""
    uuid: str = ""
    username: str = ""
    password: str = ""
    """Returned only once, on creation."""
    status: str = ""

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> CreateManagedDatabaseUserResponse:
        result: CreateManagedDatabaseUserResponse = _simple(cls, data)
        return result
