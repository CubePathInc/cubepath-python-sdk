from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

__all__ = [
    "ObjectStorageTierSummary",
    "ObjectStorageTier",
    "ObjectStorageBucket",
    "ObjectStorageBucketConnection",
    "ObjectStorageBucketUsage",
    "ObjectStorageBucketCDN",
    "ObjectStorageBucketDetail",
    "CreateObjectStorageBucketRequest",
    "CreateObjectStorageBucketResponse",
    "UpdateObjectStorageBucketRequest",
    "ObjectStorageBucketScope",
    "ObjectStorageAccessKey",
    "CreateObjectStorageAccessKeyRequest",
    "CreateObjectStorageAccessKeyResponse",
    "ObjectStorageFreeTierItem",
    "ObjectStorageTierUsage",
    "ObjectStorageBucketUsageRow",
    "ObjectStorageUsage",
]


def _simple(cls: Any, data: dict[str, Any] | None) -> Any:
    data = data or {}
    return cls(
        **{
            k: data.get(k, f.default_factory() if callable(f.default_factory) else f.default)
            for k, f in cls.__dataclass_fields__.items()
        }
    )


@dataclass
class ObjectStorageTierSummary:
    uuid: str = ""
    slug: str = ""
    name: str = ""
    media: str = ""

    @classmethod
    def from_dict(cls, data: dict[str, Any] | None) -> ObjectStorageTierSummary:
        result: ObjectStorageTierSummary = _simple(cls, data)
        return result


@dataclass
class ObjectStorageTier:
    uuid: str = ""
    slug: str = ""
    name: str = ""
    media: str = ""
    location_id: int = 0
    location_name: str = ""
    location_description: str = ""
    region: str = ""
    endpoint: str = ""
    prices: dict[str, float] = field(default_factory=dict)
    free_tier: dict[str, float] = field(default_factory=dict)
    accepting_new: bool = False

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> ObjectStorageTier:
        result: ObjectStorageTier = _simple(cls, data)
        return result


@dataclass
class ObjectStorageBucket:
    uuid: str = ""
    name: str = ""
    status: str = ""
    suspend_reason: str | None = None
    write_blocked: bool = False
    error_message: str | None = None
    project_id: int | None = None
    tier: ObjectStorageTierSummary = field(default_factory=ObjectStorageTierSummary)
    location_name: str = ""
    region: str = ""
    endpoint: str = ""
    versioning: str = ""
    protected: bool = False
    size_bytes: int = 0
    objects_count: int = 0
    usage_updated_at: str | None = None
    monthly_charges: float = 0.0
    cdn_connected: bool = False

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> ObjectStorageBucket:
        result: ObjectStorageBucket = _simple(cls, data)
        result.tier = ObjectStorageTierSummary.from_dict(data.get("tier"))
        return result


@dataclass
class ObjectStorageBucketConnection:
    endpoint: str = ""
    region: str = ""
    path_style_url: str = ""
    virtual_host_url: str = ""

    @classmethod
    def from_dict(cls, data: dict[str, Any] | None) -> ObjectStorageBucketConnection:
        result: ObjectStorageBucketConnection = _simple(cls, data)
        return result


@dataclass
class ObjectStorageBucketUsage:
    period: str = ""
    since: str = ""
    until: str = ""
    storage_gib_hours: float = 0.0
    storage_gib_month: float = 0.0
    egress_bytes: int = 0
    cdn_bytes: int = 0
    class_a_requests: int = 0
    class_b_requests: int = 0
    class_b_cdn_requests: int = 0

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> ObjectStorageBucketUsage:
        result: ObjectStorageBucketUsage = _simple(cls, data)
        return result


@dataclass
class ObjectStorageBucketCDN:
    status: str = ""
    zone_uuid: str = ""
    zone_name: str = ""
    domain: str = ""
    custom_domain: str | None = None
    zone_status: str = ""
    origin_uuid: str = ""
    origin_enabled: bool = False

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> ObjectStorageBucketCDN:
        result: ObjectStorageBucketCDN = _simple(cls, data)
        return result


@dataclass
class ObjectStorageBucketDetail(ObjectStorageBucket):
    active_at: str | None = None
    last_billed_time: str | None = None
    connection: ObjectStorageBucketConnection = field(default_factory=ObjectStorageBucketConnection)
    usage: ObjectStorageBucketUsage | None = None
    """None when usage metrics are temporarily unavailable."""
    cdn: ObjectStorageBucketCDN | None = None
    """None when no CDN origin serves the bucket."""

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> ObjectStorageBucketDetail:
        result: ObjectStorageBucketDetail = _simple(cls, data)
        result.tier = ObjectStorageTierSummary.from_dict(data.get("tier"))
        result.connection = ObjectStorageBucketConnection.from_dict(data.get("connection"))
        result.usage = ObjectStorageBucketUsage.from_dict(data["usage"]) if data.get("usage") else None
        result.cdn = ObjectStorageBucketCDN.from_dict(data["cdn"]) if data.get("cdn") else None
        return result


@dataclass
class CreateObjectStorageBucketRequest:
    name: str
    tier: str
    """Tier uuid or slug, for example "infrequent_access"."""
    project_id: int | None = None
    versioning: bool = False

    def to_dict(self) -> dict[str, Any]:
        d: dict[str, Any] = {"name": self.name, "tier": self.tier}
        if self.project_id is not None:
            d["project_id"] = self.project_id
        if self.versioning:
            d["versioning"] = True
        return d


@dataclass
class CreateObjectStorageBucketResponse:
    detail: str = ""
    uuid: str = ""
    name: str = ""
    status: str = ""
    project_id: int | None = None
    tier: ObjectStorageTierSummary = field(default_factory=ObjectStorageTierSummary)
    region: str = ""
    endpoint: str = ""

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> CreateObjectStorageBucketResponse:
        result: CreateObjectStorageBucketResponse = _simple(cls, data)
        result.tier = ObjectStorageTierSummary.from_dict(data.get("tier"))
        return result


@dataclass
class UpdateObjectStorageBucketRequest:
    versioning: str | None = None
    """"enabled" or "suspended"."""
    protected: bool | None = None

    def to_dict(self) -> dict[str, Any]:
        d: dict[str, Any] = {}
        if self.versioning is not None:
            d["versioning"] = self.versioning
        if self.protected is not None:
            d["protected"] = self.protected
        return d


@dataclass
class ObjectStorageBucketScope:
    uuid: str = ""
    name: str = ""

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> ObjectStorageBucketScope:
        result: ObjectStorageBucketScope = _simple(cls, data)
        return result


@dataclass
class ObjectStorageAccessKey:
    uuid: str = ""
    name: str = ""
    access_key_id: str = ""
    permission: str = ""
    bucket_scope: list[ObjectStorageBucketScope] | None = None
    """None means every bucket of the project in the key's tier."""
    project_id: int | None = None
    tier: ObjectStorageTierSummary = field(default_factory=ObjectStorageTierSummary)
    region: str = ""
    endpoint: str = ""
    status: str = ""
    expires_at: str | None = None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> ObjectStorageAccessKey:
        result: ObjectStorageAccessKey = _simple(cls, data)
        result.tier = ObjectStorageTierSummary.from_dict(data.get("tier"))
        scope = data.get("bucket_scope")
        result.bucket_scope = None if scope is None else [ObjectStorageBucketScope.from_dict(b) for b in scope]
        return result


@dataclass
class CreateObjectStorageAccessKeyRequest:
    name: str
    tier: str
    """Tier uuid or slug."""
    permission: str = "read_write"
    """"read_write" or "read_only"."""
    project_id: int | None = None
    bucket_uuids: list[str] | None = None
    """Limit the key to these buckets; None gives it every bucket of the project in the tier."""
    expires_at: str | None = None
    """ISO 8601 date time in the future."""

    def to_dict(self) -> dict[str, Any]:
        d: dict[str, Any] = {"name": self.name, "tier": self.tier, "permission": self.permission}
        if self.project_id is not None:
            d["project_id"] = self.project_id
        if self.bucket_uuids is not None:
            d["bucket_uuids"] = self.bucket_uuids
        if self.expires_at is not None:
            d["expires_at"] = self.expires_at
        return d


@dataclass
class CreateObjectStorageAccessKeyResponse(ObjectStorageAccessKey):
    detail: str = ""
    secret_access_key: str = ""
    """Returned only once, on creation."""

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> CreateObjectStorageAccessKeyResponse:
        result: CreateObjectStorageAccessKeyResponse = _simple(cls, data)
        result.tier = ObjectStorageTierSummary.from_dict(data.get("tier"))
        scope = data.get("bucket_scope")
        result.bucket_scope = None if scope is None else [ObjectStorageBucketScope.from_dict(b) for b in scope]
        return result


@dataclass
class ObjectStorageFreeTierItem:
    included: float = 0
    used: float | None = None

    @classmethod
    def from_dict(cls, data: dict[str, Any] | None) -> ObjectStorageFreeTierItem:
        result: ObjectStorageFreeTierItem = _simple(cls, data)
        return result


@dataclass
class ObjectStorageTierUsage:
    tier: ObjectStorageTierSummary = field(default_factory=ObjectStorageTierSummary)
    storage_gib_hours: float | None = None
    storage_gib_month: float | None = None
    egress_bytes: int | None = None
    cdn_bytes: int | None = None
    class_a_requests: int | None = None
    class_b_requests: int | None = None
    class_b_cdn_requests: int | None = None
    cost: float = 0.0
    projected_cost: float = 0.0
    free_tier: dict[str, ObjectStorageFreeTierItem] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> ObjectStorageTierUsage:
        result: ObjectStorageTierUsage = _simple(cls, data)
        result.tier = ObjectStorageTierSummary.from_dict(data.get("tier"))
        result.free_tier = {k: ObjectStorageFreeTierItem.from_dict(v) for k, v in (data.get("free_tier") or {}).items()}
        return result


@dataclass
class ObjectStorageBucketUsageRow:
    uuid: str = ""
    name: str = ""
    status: str = ""
    project_id: int | None = None
    tier_uuid: str = ""
    storage_gib_hours: float | None = None
    storage_gib_month: float | None = None
    egress_bytes: int | None = None
    cdn_bytes: int | None = None
    class_a_requests: int | None = None
    class_b_requests: int | None = None
    class_b_cdn_requests: int | None = None
    cost: float = 0.0

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> ObjectStorageBucketUsageRow:
        result: ObjectStorageBucketUsageRow = _simple(cls, data)
        return result


@dataclass
class ObjectStorageUsage:
    period: str = ""
    since: str = ""
    until: str = ""
    metrics_available: bool = False
    total_cost: float = 0.0
    projected_cost: float = 0.0
    tiers: list[ObjectStorageTierUsage] = field(default_factory=list)
    buckets: list[ObjectStorageBucketUsageRow] = field(default_factory=list)
    available_months: list[str] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> ObjectStorageUsage:
        result: ObjectStorageUsage = _simple(cls, data)
        result.tiers = [ObjectStorageTierUsage.from_dict(t) for t in data.get("tiers", [])]
        result.buckets = [ObjectStorageBucketUsageRow.from_dict(b) for b in data.get("buckets", [])]
        result.available_months = list(data.get("available_months", []))
        return result
