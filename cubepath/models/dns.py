from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

__all__ = [
    "DNSZone",
    "DNSRecord",
    "SOARecord",
    "ZoneVerifyResponse",
    "ZoneScanResponse",
    "CreateDNSZoneRequest",
    "CreateDNSRecordRequest",
    "UpdateDNSRecordRequest",
    "UpdateSOARequest",
]


@dataclass
class DNSZone:
    uuid: str = ""
    domain: str = ""
    status: str = ""
    records_count: int = 0
    nameservers: list[str] = field(default_factory=list)
    project_id: str = ""
    created_at: str = ""

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> DNSZone:
        return cls(**{k: data.get(k, f.default) for k, f in cls.__dataclass_fields__.items()})


@dataclass
class DNSRecord:
    uuid: str = ""
    zone_uuid: str = ""
    name: str = ""
    record_type: str = ""
    type: str = ""
    content: str = ""
    ttl: int = 0
    priority: int | None = None
    weight: int | None = None
    port: int | None = None
    comment: str = ""

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> DNSRecord:
        return cls(
            uuid=data.get("uuid", ""),
            zone_uuid=data.get("zone_uuid", ""),
            name=data.get("name", ""),
            record_type=data.get("record_type", ""),
            type=data.get("type", ""),
            content=data.get("content", ""),
            ttl=data.get("ttl", 0),
            priority=data.get("priority"),
            weight=data.get("weight"),
            port=data.get("port"),
            comment=data.get("comment", ""),
        )


@dataclass
class SOARecord:
    primary_ns: str = ""
    hostmaster: str = ""
    serial: int = 0
    refresh: int = 0
    retry: int = 0
    expire: int = 0
    minimum: int = 0

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> SOARecord:
        return cls(**{k: data.get(k, f.default) for k, f in cls.__dataclass_fields__.items()})


@dataclass
class ZoneVerifyResponse:
    verified: bool = False
    message: str = ""
    next_check_at: str = ""

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> ZoneVerifyResponse:
        return cls(**{k: data.get(k, f.default) for k, f in cls.__dataclass_fields__.items()})


@dataclass
class ZoneScanResponse:
    imported: int = 0
    skipped: int = 0
    errors: list[str] = field(default_factory=list)
    records: list[DNSRecord] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> ZoneScanResponse:
        return cls(
            imported=data.get("imported", 0),
            skipped=data.get("skipped", 0),
            errors=data.get("errors", []),
            records=[DNSRecord.from_dict(r) for r in data.get("records", [])],
        )


@dataclass
class CreateDNSZoneRequest:
    domain: str
    project_id: str = ""

    def to_dict(self) -> dict[str, Any]:
        d: dict[str, Any] = {"domain": self.domain}
        if self.project_id:
            d["project_id"] = self.project_id
        return d


@dataclass
class CreateDNSRecordRequest:
    name: str
    record_type: str
    content: str
    ttl: int
    priority: int | None = None
    weight: int | None = None
    port: int | None = None
    comment: str = ""

    def to_dict(self) -> dict[str, Any]:
        d: dict[str, Any] = {
            "name": self.name,
            "record_type": self.record_type,
            "content": self.content,
            "ttl": self.ttl,
        }
        if self.priority is not None:
            d["priority"] = self.priority
        if self.weight is not None:
            d["weight"] = self.weight
        if self.port is not None:
            d["port"] = self.port
        if self.comment:
            d["comment"] = self.comment
        return d


@dataclass
class UpdateDNSRecordRequest:
    name: str = ""
    content: str = ""
    ttl: int | None = None
    priority: int | None = None

    def to_dict(self) -> dict[str, Any]:
        d: dict[str, Any] = {}
        if self.name:
            d["name"] = self.name
        if self.content:
            d["content"] = self.content
        if self.ttl is not None:
            d["ttl"] = self.ttl
        if self.priority is not None:
            d["priority"] = self.priority
        return d


@dataclass
class UpdateSOARequest:
    refresh: int | None = None
    retry: int | None = None
    expire: int | None = None
    minimum: int | None = None
    hostmaster: str = ""

    def to_dict(self) -> dict[str, Any]:
        d: dict[str, Any] = {}
        if self.refresh is not None:
            d["refresh"] = self.refresh
        if self.retry is not None:
            d["retry"] = self.retry
        if self.expire is not None:
            d["expire"] = self.expire
        if self.minimum is not None:
            d["minimum"] = self.minimum
        if self.hostmaster:
            d["hostmaster"] = self.hostmaster
        return d
