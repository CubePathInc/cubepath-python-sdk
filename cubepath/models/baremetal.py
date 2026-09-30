from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

__all__ = [
    "Baremetal",
    "BaremetalModel",
    "OSInfo",
    "SSHKeyRef",
    "CreateBaremetalRequest",
    "UpdateBaremetalRequest",
    "ReinstallBaremetalRequest",
    "RescueResponse",
    "BMCSensors",
    "SensorReading",
    "IPMISession",
    "ReinstallStatus",
    "BaremetalKVM",
    "BaremetalDiskLayoutOption",
    "BaremetalOSOption",
    "BaremetalModelOption",
    "BaremetalModelLocation",
]


@dataclass
class BaremetalModel:
    id: str = ""
    model_name: str = ""
    cpu: int = 0
    cpu_specs: str = ""
    cpu_bench: int = 0
    ram: int = 0
    ram_size: str = ""
    ram_type: str = ""
    storage_type: str = ""
    disk_count: int = 0
    disk_size: str = ""
    disk_type: str = ""
    port: str = ""
    kvm: bool = False
    price: str = ""

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> BaremetalModel:
        return cls(**{k: data.get(k, f.default) for k, f in cls.__dataclass_fields__.items()})


@dataclass
class OSInfo:
    id: str = ""
    name: str = ""
    version: str = ""

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> OSInfo:
        return cls(**{k: data.get(k, f.default) for k, f in cls.__dataclass_fields__.items()})


@dataclass
class SSHKeyRef:
    name: str = ""

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> SSHKeyRef:
        return cls(name=data.get("name", ""))


@dataclass
class Baremetal:
    id: str = ""
    hostname: str = ""
    label: str = ""
    project_id: str = ""
    status: str = ""
    user: str = ""
    os: OSInfo | None = None
    location: Any = None
    baremetal_model: BaremetalModel | None = None
    floating_ips: list[Any] = field(default_factory=list)
    monitoring_enable: bool = False
    ssh_username: str = ""
    ssh_key: str = ""
    created_at: str = ""

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Baremetal:
        return cls(
            id=data.get("id", ""),
            hostname=data.get("hostname", ""),
            label=data.get("label", ""),
            project_id=data.get("project_id", ""),
            status=data.get("status", ""),
            user=data.get("user", ""),
            os=OSInfo.from_dict(data["os"]) if data.get("os") else None,
            location=data.get("location"),
            baremetal_model=BaremetalModel.from_dict(data["baremetal_model"]) if data.get("baremetal_model") else None,
            floating_ips=data.get("floating_ips", []),
            monitoring_enable=data.get("monitoring_enable", False),
            ssh_username=data.get("ssh_username", ""),
            ssh_key=data.get("ssh_key", ""),
            created_at=data.get("created_at", ""),
        )


@dataclass
class CreateBaremetalRequest:
    model_name: str
    location_name: str
    hostname: str
    password: str
    label: str = ""
    user: str = ""
    ssh_key_ids: list[int] = field(default_factory=list)
    os_name: str = ""
    disk_layout_name: str = ""

    def to_dict(self) -> dict[str, Any]:
        d: dict[str, Any] = {
            "model_name": self.model_name,
            "location_name": self.location_name,
            "hostname": self.hostname,
            "password": self.password,
        }
        if self.label:
            d["label"] = self.label
        if self.user:
            d["user"] = self.user
        if self.ssh_key_ids:
            d["ssh_key_ids"] = self.ssh_key_ids
        if self.os_name:
            d["os_name"] = self.os_name
        if self.disk_layout_name:
            d["disk_layout_name"] = self.disk_layout_name
        return d


@dataclass
class UpdateBaremetalRequest:
    hostname: str = ""
    label: str = ""
    tags: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        d: dict[str, Any] = {}
        if self.hostname:
            d["hostname"] = self.hostname
        if self.label:
            d["label"] = self.label
        if self.tags:
            d["tags"] = self.tags
        return d


@dataclass
class ReinstallBaremetalRequest:
    os_name: str
    password: str
    disk_layout_name: str = ""
    user: str = ""
    hostname: str = ""
    ssh_key_ids: list[int] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        d: dict[str, Any] = {"os_name": self.os_name, "password": self.password}
        if self.disk_layout_name:
            d["disk_layout_name"] = self.disk_layout_name
        if self.user:
            d["user"] = self.user
        if self.hostname:
            d["hostname"] = self.hostname
        if self.ssh_key_ids:
            d["ssh_key_ids"] = self.ssh_key_ids
        return d


@dataclass
class RescueResponse:
    detail: str = ""
    username: str = ""
    password: str = ""

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> RescueResponse:
        return cls(**{k: data.get(k, f.default) for k, f in cls.__dataclass_fields__.items()})


@dataclass
class SensorReading:
    name: str = ""
    value: float = 0.0
    # CELSIUS for temperatures, RPM for fans.
    unit: str = ""

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> SensorReading:
        return cls(**{k: data.get(k, f.default) for k, f in cls.__dataclass_fields__.items()})


@dataclass
class BMCSensors:
    # Deprecated: no longer returned by the API; always empty.
    node: str = ""
    # False when the BMC has not been polled recently (see last_seen).
    ipmi_available: bool = False
    power_on: bool = False
    sensors: dict[str, list[SensorReading]] = field(default_factory=dict)
    # Unix time of the last BMC poll, None when never polled.
    last_seen: int | None = None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> BMCSensors:
        sensors_raw = data.get("sensors", {})
        sensors: dict[str, list[SensorReading]] = {}
        for key in ("temperatures", "fans"):
            sensors[key] = [SensorReading.from_dict(s) for s in sensors_raw.get(key, [])]
        return cls(
            node=data.get("node", ""),
            ipmi_available=data.get("ipmi_available", False),
            power_on=data.get("power_on", False),
            sensors=sensors,
            last_seen=data.get("last_seen"),
        )


@dataclass
class IPMISession:
    proxy_url: str = ""
    credentials: dict[str, str] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> IPMISession:
        return cls(
            proxy_url=data.get("proxy_url", ""),
            credentials=data.get("credentials", {}),
        )


@dataclass
class ReinstallStatus:
    is_reinstalling: bool = False
    status: str = ""
    # Deprecated: no longer available; always empty.
    os_name: str = ""

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> ReinstallStatus:
        return cls(**{k: data.get(k, f.default) for k, f in cls.__dataclass_fields__.items()})


@dataclass
class BaremetalKVM:
    """KVM-over-IP console access."""

    url: str = ""
    username: str = ""
    password: str | None = None
    updated_at: str | None = None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> BaremetalKVM:
        return cls(**{k: data.get(k, f.default) for k, f in cls.__dataclass_fields__.items()})


@dataclass
class BaremetalDiskLayoutOption:
    id: int = 0
    name: str = ""
    disk_layout_name: str = ""
    disk_type: str | None = None
    raid_type: str | None = None
    disk_count: int | None = None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> BaremetalDiskLayoutOption:
        return cls(**{k: data.get(k, f.default) for k, f in cls.__dataclass_fields__.items()})


@dataclass
class BaremetalOSOption:
    """An operating system that can be installed on a server, with its disk layouts."""

    id: int = 0
    os_name: str = ""
    operating_system: str | None = None
    disk_layouts: list[BaremetalDiskLayoutOption] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> BaremetalOSOption:
        return cls(
            id=data.get("id", 0),
            os_name=data.get("os_name", ""),
            operating_system=data.get("operating_system"),
            disk_layouts=[BaremetalDiskLayoutOption.from_dict(d) for d in data.get("disk_layouts", [])],
        )


@dataclass
class BaremetalModelOption:
    model_name: str = ""
    price: float = 0.0
    """Monthly."""
    discount_value: float = 0.0
    discount_type: str | None = None
    cpu: str = ""
    cpu_specs: str = ""
    cpu_bench: float | None = None
    ram_size: int = 0
    ram_type: str = ""
    disk_size: str = ""
    disk_type: str | None = None
    port: int = 0
    setup: float = 0.0
    kvm: str = ""
    stock_available: int = 0

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> BaremetalModelOption:
        return cls(**{k: data.get(k, f.default) for k, f in cls.__dataclass_fields__.items()})


@dataclass
class BaremetalModelLocation:
    location_name: str = ""
    description: str = ""
    models: list[BaremetalModelOption] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> BaremetalModelLocation:
        return cls(
            location_name=data.get("location_name", ""),
            description=data.get("description", ""),
            models=[BaremetalModelOption.from_dict(m) for m in data.get("models", [])],
        )
