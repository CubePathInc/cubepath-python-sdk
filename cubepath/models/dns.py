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
    "DNSRegion",
    "DNSHealthCheck",
    "UpsertDNSHealthCheckRequest",
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
    region: str | None = None
    """GeoDNS region; None means global."""
    created_at: str = ""
    updated_at: str = ""

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
            comment=data.get("comment") or "",
            region=data.get("region"),
            created_at=data.get("created_at", ""),
            updated_at=data.get("updated_at", ""),
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
    detail: str = ""
    # Deprecated: the API returns ``detail``; kept for compatibility, always empty.
    message: str = ""
    next_check_at: str | None = None

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
    region: str = ""
    """GeoDNS region code (see list_regions); empty means global. Pro and Business tiers only."""

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
        if self.region:
            d["region"] = self.region
        return d


@dataclass
class UpdateDNSRecordRequest:
    name: str = ""
    content: str = ""
    ttl: int | None = None
    priority: int | None = None
    weight: int | None = None
    port: int | None = None
    comment: str | None = None
    region: str | None = None
    """GeoDNS region code; "global" serves the record everywhere."""

    def to_dict(self) -> dict[str, Any]:
        d: dict[str, Any] = {}
        if self.name:
            d["name"] = self.name
        if self.content:
            d["content"] = self.content
        for k in ("ttl", "priority", "weight", "port", "comment", "region"):
            v = getattr(self, k)
            if v is not None:
                d[k] = v
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


# ── GeoDNS and health checks ─────────────────────────────────────


@dataclass
class DNSRegion:
    code: str = ""
    name: str = ""

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> DNSRegion:
        return cls(**{k: data.get(k, f.default) for k, f in cls.__dataclass_fields__.items()})


@dataclass
class DNSHealthCheck:
    uuid: str = ""
    record_uuid: str = ""
    name: str = ""
    check_type: str = ""
    """http, https, tcp or ping."""
    target: str | None = None
    port: int | None = None
    path: str | None = None
    expected_status: int | None = None
    interval_secs: int = 0
    timeout_secs: int = 0
    healthy_threshold: int = 0
    unhealthy_threshold: int = 0
    enabled: bool = True
    last_status: str = ""
    """healthy, unhealthy or unknown."""
    last_check_at: str | None = None
    created_at: str = ""
    updated_at: str = ""

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> DNSHealthCheck:
        return cls(**{k: data.get(k, f.default) for k, f in cls.__dataclass_fields__.items()})


@dataclass
class UpsertDNSHealthCheckRequest:
    """Health check of a record: while unhealthy the record is left out of the answers.

    Pro and Business tiers only, billed while enabled.
    """

    name: str
    check_type: str
    """http, https, tcp or ping."""
    target: str | None = None
    """Host or IP to check; defaults to the record content."""
    port: int | None = None
    """Required for tcp."""
    path: str | None = None
    expected_status: int | None = 200
    interval_secs: int = 60
    timeout_secs: int = 5
    healthy_threshold: int = 2
    unhealthy_threshold: int = 3
    enabled: bool = True

    def to_dict(self) -> dict[str, Any]:
        d: dict[str, Any] = {}
        for k in self.__dataclass_fields__:
            v = getattr(self, k)
            if v is not None:
                d[k] = v
        return d
