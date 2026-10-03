from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

__all__ = [
    "ObjectStorageTierSummary",
    "ObjectStorageTier",
    "ObjectStorageLockRetention",
    "ObjectStorageObjectLock",
    "ObjectStorageBucket",
    "ObjectStorageBucketConnection",
    "ObjectStorageBucketUsage",
    "ObjectStorageBucketCDN",
    "ObjectStorageBucketDetail",
    "CreateObjectStorageBucketRequest",
    "CreateObjectStorageBucketResponse",
    "UpdateObjectStorageBucketRequest",
    "SetObjectStorageObjectLockRequest",
    "ObjectStorageBucketScope",
    "ObjectStorageAccessKey",
    "CreateObjectStorageAccessKeyRequest",
    "CreateObjectStorageAccessKeyResponse",
    "ObjectStorageFreeTierItem",
    "ObjectStorageTierUsage",
    "ObjectStorageBucketUsageRow",
    "ObjectStorageUsage",
    "ObjectStorageEventDestination",
    "ObjectStorageEventDestinationSecret",
    "CreateObjectStorageEventDestinationRequest",
    "UpdateObjectStorageEventDestinationRequest",
    "ObjectStorageEventRule",
    "CreateObjectStorageEventRuleRequest",
    "UpdateObjectStorageEventRuleRequest",
    "ObjectStorageEventDelivery",
    "ObjectStorageEventDeliveries",
    "ObjectStorageReplicationTag",
    "ObjectStorageReplicationSource",
    "ObjectStorageReplicationDestination",
    "ObjectStorageReplicationRules",
    "ObjectStorageReplicationBackfill",
    "ObjectStorageReplicationMetrics",
    "ObjectStorageReplication",
    "ObjectStorageReplicationDetail",
    "ObjectStorageReplicationDestinationRequest",
    "CreateObjectStorageReplicationRequest",
    "CreateObjectStorageReplicationResponse",
    "UpdateObjectStorageReplicationRequest",
    "ObjectStorageReplicationGrant",
    "CreateObjectStorageReplicationGrantRequest",
    "CreateObjectStorageReplicationGrantResponse",
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
class ObjectStorageLockRetention:
    """An Object Lock default retention. ``mode`` is "governance" (keys with ``bypass_governance``
    can still delete early) or "compliance" (nobody can delete or shorten it before the date).
    Set exactly one of ``days`` or ``years``."""

    mode: str = "governance"
    days: int | None = None
    years: int | None = None

    @classmethod
    def from_dict(cls, data: dict[str, Any] | None) -> ObjectStorageLockRetention:
        result: ObjectStorageLockRetention = _simple(cls, data)
        return result

    def to_dict(self) -> dict[str, Any]:
        d: dict[str, Any] = {"mode": self.mode}
        if self.days is not None:
            d["days"] = self.days
        if self.years is not None:
            d["years"] = self.years
        return d


@dataclass
class ObjectStorageObjectLock:
    enabled: bool = False
    default_retention: ObjectStorageLockRetention | None = None
    """None when the bucket has no default retention."""

    @classmethod
    def from_dict(cls, data: dict[str, Any] | None) -> ObjectStorageObjectLock:
        data = data or {}
        rule = data.get("default_retention")
        return cls(
            enabled=bool(data.get("enabled", False)),
            default_retention=ObjectStorageLockRetention.from_dict(rule) if rule else None,
        )


@dataclass
class ObjectStorageBucketEncryption:
    """Encryption at rest of a bucket: ``algorithm`` "AES256" (SSE-S3) and ``scope``
    "all_objects", or "new_objects" while objects written before the bucket default may still be
    stored unencrypted."""

    algorithm: str = "AES256"
    scope: str = "all_objects"

    @classmethod
    def from_dict(cls, data: dict[str, Any] | None) -> ObjectStorageBucketEncryption | None:
        if not data:
            return None
        result: ObjectStorageBucketEncryption = _simple(cls, data)
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
    object_lock: ObjectStorageObjectLock = field(default_factory=ObjectStorageObjectLock)
    """Object Lock state: chosen when the bucket is created, never added later."""
    locked_content_kept: bool = False
    """The last delete left versions protected by Object Lock (retention or legal hold): the
    bucket stays and keeps being billed until they expire. Cleared by the next delete."""
    encryption: ObjectStorageBucketEncryption | None = None
    """Encryption at rest; None until the bucket default is applied."""

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> ObjectStorageBucket:
        result: ObjectStorageBucket = _simple(cls, data)
        result.tier = ObjectStorageTierSummary.from_dict(data.get("tier"))
        result.object_lock = ObjectStorageObjectLock.from_dict(data.get("object_lock"))
        result.encryption = ObjectStorageBucketEncryption.from_dict(data.get("encryption"))
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
        result.object_lock = ObjectStorageObjectLock.from_dict(data.get("object_lock"))
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
    object_lock: bool = False
    """Create the bucket with Object Lock (WORM). Only possible now, never later. It implies
    versioning and the bucket is created with deletion protection on."""
    object_lock_default: ObjectStorageLockRetention | None = None
    """Default retention of new objects (only with object_lock)."""
    accept_object_lock_terms: bool = False
    """Must be True with object_lock: you accept the Object Lock terms."""

    def to_dict(self) -> dict[str, Any]:
        d: dict[str, Any] = {"name": self.name, "tier": self.tier}
        if self.project_id is not None:
            d["project_id"] = self.project_id
        if self.versioning or self.object_lock:
            d["versioning"] = True
        if self.object_lock:
            d["object_lock"] = True
        if self.object_lock_default is not None:
            d["object_lock_default"] = self.object_lock_default.to_dict()
        if self.accept_object_lock_terms:
            d["accept_object_lock_terms"] = True
        return d


@dataclass
class SetObjectStorageObjectLockRequest:
    default_retention: ObjectStorageLockRetention | None = None
    """The new default retention, or None to remove it (a compliance rule can only be kept or
    lengthened)."""
    accept_object_lock_terms: bool = False
    """Required (True) when the change turns compliance on or lengthens the retention."""

    def to_dict(self) -> dict[str, Any]:
        return {
            "default_retention": self.default_retention.to_dict() if self.default_retention else None,
            "accept_object_lock_terms": self.accept_object_lock_terms,
        }


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
    object_lock: ObjectStorageObjectLock = field(default_factory=ObjectStorageObjectLock)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> CreateObjectStorageBucketResponse:
        result: CreateObjectStorageBucketResponse = _simple(cls, data)
        result.tier = ObjectStorageTierSummary.from_dict(data.get("tier"))
        result.object_lock = ObjectStorageObjectLock.from_dict(data.get("object_lock"))
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
    bypass_governance: bool = False
    """read_write keys only: may delete versions under governance retention."""

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
    bypass_governance: bool = False
    """read_write keys only: the key may delete versions under governance retention (sending
    x-amz-bypass-governance-retention: true). Cannot be changed later."""

    def to_dict(self) -> dict[str, Any]:
        d: dict[str, Any] = {"name": self.name, "tier": self.tier, "permission": self.permission}
        if self.project_id is not None:
            d["project_id"] = self.project_id
        if self.bucket_uuids is not None:
            d["bucket_uuids"] = self.bucket_uuids
        if self.expires_at is not None:
            d["expires_at"] = self.expires_at
        if self.bypass_governance:
            d["bypass_governance"] = True
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


@dataclass
class ObjectStorageLifecycle:
    """Lifecycle of a bucket. status: none, pending, active, paused (bucket blocked or on hold)
    or error. rules are dicts in the API format: {"id", "enabled", "filter", "expiration",
    "noncurrent_version_expiration", "abort_incomplete_multipart_upload"}."""

    bucket_uuid: str = ""
    status: str = "none"
    rules: list[dict[str, Any]] = field(default_factory=list)
    platform_rules: list[dict[str, Any]] = field(default_factory=list)
    generation: int = 0
    applied_generation: int = 0
    error: str | None = None
    updated_at: str | None = None
    notes: list[str] = field(default_factory=list)

    @property
    def applied(self) -> bool:
        """Whether the latest change of the rules reached the storage service."""
        return self.applied_generation >= self.generation

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> ObjectStorageLifecycle:
        result: ObjectStorageLifecycle = _simple(cls, data)
        result.rules = list(data.get("rules") or [])
        result.platform_rules = list(data.get("platform_rules") or [])
        result.notes = list(data.get("notes") or [])
        return result


# ── Event notifications ──────────────────────────────────────────


@dataclass
class ObjectStorageEventDestination:
    """Where bucket events are delivered: a signed webhook ("webhook") or a Cloud Alerts channel
    ("notificator"). The webhook URL is never returned in clear (url_masked)."""

    uuid: str = ""
    name: str = ""
    type: str = ""
    url_masked: str | None = None
    notificator: dict[str, Any] | None = None
    """{"id", "name", "type"} of the channel of a "notificator" destination."""
    payload_format: str = "cubepath"
    status: str = ""
    """active, disabled, auto_disabled or deleted."""
    disabled_reason: str | None = None
    previous_secret_expires_at: str | None = None
    """Until when the secret before the last rotation still signs."""
    last_success_at: str | None = None
    last_failure_at: str | None = None
    last_error: str | None = None
    rules_count: int = 0
    created_at: str | None = None

    @classmethod
    def from_dict(cls, data: dict[str, Any] | None) -> ObjectStorageEventDestination:
        result: ObjectStorageEventDestination = _simple(cls, data)
        return result


@dataclass
class ObjectStorageEventDestinationSecret:
    """Answer of create and rotate-secret, the only calls that return the signing secret
    (None for a channel destination)."""

    destination: ObjectStorageEventDestination = field(default_factory=ObjectStorageEventDestination)
    signing_secret: str | None = None
    previous_secret_expires_at: str | None = None
    """Only after a rotation: the previous secret signs until then."""

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> ObjectStorageEventDestinationSecret:
        return cls(
            destination=ObjectStorageEventDestination.from_dict(data.get("destination")),
            signing_secret=data.get("signing_secret"),
            previous_secret_expires_at=data.get("previous_secret_expires_at"),
        )


@dataclass
class CreateObjectStorageEventDestinationRequest:
    name: str
    type: str
    """"webhook" (with url) or "notificator" (with notificator_id, a Cloud Alerts channel)."""
    url: str | None = None
    notificator_id: str | None = None
    payload_format: str | None = None
    """"cubepath" (default) or "s3"."""

    def to_dict(self) -> dict[str, Any]:
        d: dict[str, Any] = {"name": self.name, "type": self.type}
        if self.url is not None:
            d["url"] = self.url
        if self.notificator_id is not None:
            d["notificator_id"] = self.notificator_id
        if self.payload_format is not None:
            d["payload_format"] = self.payload_format
        return d


@dataclass
class UpdateObjectStorageEventDestinationRequest:
    name: str | None = None
    url: str | None = None
    payload_format: str | None = None
    enabled: bool | None = None

    def to_dict(self) -> dict[str, Any]:
        return {k: v for k, v in self.__dict__.items() if v is not None}


@dataclass
class ObjectStorageEventRule:
    """Sends a bucket's events of the listed types whose key matches prefix and suffix to a
    destination. Applied asynchronously: status goes from "pending" to "active"."""

    uuid: str = ""
    name: str = ""
    bucket_uuid: str = ""
    destination: dict[str, Any] = field(default_factory=dict)
    """{"uuid", "name", "type"}, empty when unknown."""
    events: list[str] = field(default_factory=list)
    prefix: str = ""
    suffix: str = ""
    enabled: bool = True
    status: str = ""
    error_message: str | None = None
    created_at: str | None = None

    @classmethod
    def from_dict(cls, data: dict[str, Any] | None) -> ObjectStorageEventRule:
        result: ObjectStorageEventRule = _simple(cls, data)
        result.destination = dict(result.destination or {})
        result.events = list(result.events or [])
        return result


@dataclass
class ObjectStorageEventDelivery:
    """One delivery attempt. status: success, failed (retried later) or dead (given up)."""

    ts: str = ""
    ts_ms: int = 0
    event_id: str = ""
    delivery_id: str = ""
    event_type: str = ""
    bucket_uuid: str = ""
    bucket_name: str | None = None
    rule_uuid: str = ""
    object_key: str = ""
    attempt: int = 0
    status: str = ""
    http_status: int = 0
    latency_ms: int = 0
    error: str = ""

    @classmethod
    def from_dict(cls, data: dict[str, Any] | None) -> ObjectStorageEventDelivery:
        result: ObjectStorageEventDelivery = _simple(cls, data)
        return result


@dataclass
class ObjectStorageEventDeliveries:
    """A page of the delivery history, newest first. Pass next_before as before for the next
    (older) page; None on the last page."""

    deliveries: list[ObjectStorageEventDelivery] = field(default_factory=list)
    next_before: int | None = None

    @classmethod
    def from_dict(cls, data: dict[str, Any] | None) -> ObjectStorageEventDeliveries:
        data = data or {}
        return cls(
            deliveries=[ObjectStorageEventDelivery.from_dict(d) for d in data.get("deliveries") or []],
            next_before=data.get("next_before"),
        )


@dataclass
class CreateObjectStorageEventRuleRequest:
    name: str
    destination_uuid: str
    events: list[str]
    """object.created, object.removed and/or object.tagging."""
    prefix: str = ""
    suffix: str = ""
    enabled: bool = True

    def to_dict(self) -> dict[str, Any]:
        d: dict[str, Any] = {
            "name": self.name,
            "destination_uuid": self.destination_uuid,
            "events": list(self.events),
            "enabled": self.enabled,
        }
        if self.prefix:
            d["prefix"] = self.prefix
        if self.suffix:
            d["suffix"] = self.suffix
        return d


@dataclass
class UpdateObjectStorageEventRuleRequest:
    name: str | None = None
    destination_uuid: str | None = None
    events: list[str] | None = None
    prefix: str | None = None
    suffix: str | None = None
    enabled: bool | None = None

    def to_dict(self) -> dict[str, Any]:
        return {k: v for k, v in self.__dict__.items() if v is not None}


@dataclass
class ObjectStorageLifecycleChange:
    """Answer of put/delete_bucket_lifecycle; generation is None when nothing changed."""

    detail: str = ""
    generation: int | None = None
    notes: list[str] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> ObjectStorageLifecycleChange:
        result: ObjectStorageLifecycleChange = _simple(cls, data)
        result.notes = list(data.get("notes") or [])
        return result


# ── Replication ───────────────────────────────────────────────────


@dataclass
class ObjectStorageReplicationTag:
    key: str = ""
    value: str = ""

    @classmethod
    def from_dict(cls, data: dict[str, Any] | None) -> ObjectStorageReplicationTag:
        result: ObjectStorageReplicationTag = _simple(cls, data)
        return result

    def to_dict(self) -> dict[str, Any]:
        return {"key": self.key, "value": self.value}


@dataclass
class ObjectStorageReplicationSource:
    """Source bucket. For an incoming replication of another organization bucket_uuid and
    project_id are None (only the names are shown)."""

    bucket_uuid: str | None = None
    bucket_name: str | None = None
    project_id: int | None = None
    organization_name: str | None = None
    same_organization: bool = False

    @classmethod
    def from_dict(cls, data: dict[str, Any] | None) -> ObjectStorageReplicationSource:
        result: ObjectStorageReplicationSource = _simple(cls, data)
        return result


@dataclass
class ObjectStorageReplicationDestination:
    """Destination of a replication. ``type`` "cubepath" fills the bucket_* fields, "external"
    the provider, endpoint, region, bucket, path_style and the masked access_key_id (the secret is
    never returned)."""

    type: str = ""
    bucket_uuid: str | None = None
    bucket_name: str | None = None
    project_id: int | None = None
    """Only when the destination bucket is in your organization."""
    organization_name: str | None = None
    same_organization: bool = False
    provider: str | None = None
    endpoint: str | None = None
    region: str | None = None
    bucket: str | None = None
    path_style: str | None = None
    access_key_id: str | None = None
    """Masked: **** and the last 4 characters."""

    @classmethod
    def from_dict(cls, data: dict[str, Any] | None) -> ObjectStorageReplicationDestination:
        result: ObjectStorageReplicationDestination = _simple(cls, data)
        return result


@dataclass
class ObjectStorageReplicationRules:
    enabled: bool = False
    prefix: str | None = None
    tags: list[ObjectStorageReplicationTag] = field(default_factory=list)
    delete_marker_replication: bool = False
    delete_replication: bool = False
    existing_objects: bool = False

    @classmethod
    def from_dict(cls, data: dict[str, Any] | None) -> ObjectStorageReplicationRules:
        result: ObjectStorageReplicationRules = _simple(cls, data)
        result.tags = [ObjectStorageReplicationTag.from_dict(t) for t in (data or {}).get("tags") or []]
        return result


@dataclass
class ObjectStorageReplicationBackfill:
    """Copy of the objects the bucket already held. status: none, queued, running, completed or
    failed. objects, bytes and failed_objects add up over every attempt and resync."""

    status: str = "none"
    started_at: str | None = None
    finished_at: str | None = None
    objects: int = 0
    bytes: int = 0
    failed_objects: int = 0

    @classmethod
    def from_dict(cls, data: dict[str, Any] | None) -> ObjectStorageReplicationBackfill:
        result: ObjectStorageReplicationBackfill = _simple(cls, data)
        return result


@dataclass
class ObjectStorageReplicationMetrics:
    replicated_bytes_24h: int | None = None
    replicated_objects_24h: int | None = None
    failed_objects_1h: int | None = None
    queued_objects: int | None = None
    queued_bytes: int | None = None
    last_sample_at: str | None = None
    egress_bytes_month: int | None = None
    """External destinations only."""

    @classmethod
    def from_dict(cls, data: dict[str, Any] | None) -> ObjectStorageReplicationMetrics:
        result: ObjectStorageReplicationMetrics = _simple(cls, data)
        return result


@dataclass
class ObjectStorageReplication:
    """A bucket replication. status: pending, active, paused (see pause_reason), suspended, error
    or deleting. pause_reason: customer, org, abuse, admin, source_blocked or dest_revoked.
    direction: outgoing (the source bucket is yours) or incoming. health: unknown, ok, lagging or
    failing."""

    uuid: str = ""
    status: str = ""
    pause_reason: str | None = None
    direction: str = ""
    source: ObjectStorageReplicationSource = field(default_factory=ObjectStorageReplicationSource)
    destination: ObjectStorageReplicationDestination = field(default_factory=ObjectStorageReplicationDestination)
    rules: ObjectStorageReplicationRules = field(default_factory=ObjectStorageReplicationRules)
    health: str = "unknown"
    health_reason: str | None = None
    health_checked_at: str | None = None
    backfill: ObjectStorageReplicationBackfill = field(default_factory=ObjectStorageReplicationBackfill)
    error_message: str | None = None
    created_at: str | None = None
    active_at: str | None = None

    def _nested(self, data: dict[str, Any]) -> None:
        self.source = ObjectStorageReplicationSource.from_dict(data.get("source"))
        self.destination = ObjectStorageReplicationDestination.from_dict(data.get("destination"))
        self.rules = ObjectStorageReplicationRules.from_dict(data.get("rules"))
        self.backfill = ObjectStorageReplicationBackfill.from_dict(data.get("backfill"))

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> ObjectStorageReplication:
        result: ObjectStorageReplication = _simple(cls, data)
        result._nested(data)
        return result


@dataclass
class ObjectStorageReplicationDetail(ObjectStorageReplication):
    metrics: ObjectStorageReplicationMetrics | None = None
    """None when metrics are unavailable or there is no sample yet."""

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> ObjectStorageReplicationDetail:
        result: ObjectStorageReplicationDetail = _simple(cls, data)
        result._nested(data)
        result.metrics = ObjectStorageReplicationMetrics.from_dict(data["metrics"]) if data.get("metrics") else None
        return result


@dataclass
class ObjectStorageReplicationDestinationRequest:
    """Where to replicate. ``type`` "cubepath": bucket_uuid (plus grant_token when the bucket
    belongs to another organization). ``type`` "external": endpoint (public HTTPS host, port 443
    only), region, bucket, access_key_id and secret_access_key; provider ("aws", "wasabi" or
    "other") and path_style ("auto", "on" or "off") are optional. Use the helpers
    :meth:`cubepath` and :meth:`external`."""

    type: str
    bucket_uuid: str | None = None
    grant_token: str | None = None
    provider: str | None = None
    endpoint: str | None = None
    region: str | None = None
    bucket: str | None = None
    path_style: str | None = None
    access_key_id: str | None = None
    secret_access_key: str | None = field(default=None, repr=False)
    """Never returned by the API."""

    @classmethod
    def cubepath(cls, bucket_uuid: str, grant_token: str | None = None) -> ObjectStorageReplicationDestinationRequest:
        return cls(type="cubepath", bucket_uuid=bucket_uuid, grant_token=grant_token)

    @classmethod
    def external(
        cls,
        *,
        endpoint: str,
        region: str,
        bucket: str,
        access_key_id: str,
        secret_access_key: str,
        provider: str | None = None,
        path_style: str | None = None,
    ) -> ObjectStorageReplicationDestinationRequest:
        return cls(
            type="external",
            endpoint=endpoint,
            region=region,
            bucket=bucket,
            access_key_id=access_key_id,
            secret_access_key=secret_access_key,
            provider=provider,
            path_style=path_style,
        )

    def to_dict(self) -> dict[str, Any]:
        d: dict[str, Any] = {"type": self.type}
        for k in (
            "bucket_uuid",
            "grant_token",
            "provider",
            "endpoint",
            "region",
            "bucket",
            "path_style",
            "access_key_id",
            "secret_access_key",
        ):
            v = getattr(self, k)
            if v is not None:
                d[k] = v
        return d


@dataclass
class CreateObjectStorageReplicationRequest:
    """Replicate a versioned bucket to one destination. Filter by prefix or by tags, not both;
    delete markers cannot be replicated with a tag filter."""

    source_bucket_uuid: str
    destination: ObjectStorageReplicationDestinationRequest
    prefix: str | None = None
    tags: list[ObjectStorageReplicationTag] | None = None
    delete_marker_replication: bool = False
    delete_replication: bool = False
    existing_objects: bool = True
    """Copy the objects the bucket already holds."""

    def to_dict(self) -> dict[str, Any]:
        d: dict[str, Any] = {
            "source_bucket_uuid": self.source_bucket_uuid,
            "destination": self.destination.to_dict(),
            "delete_marker_replication": self.delete_marker_replication,
            "delete_replication": self.delete_replication,
            "existing_objects": self.existing_objects,
        }
        if self.prefix is not None:
            d["prefix"] = self.prefix
        if self.tags is not None:
            d["tags"] = [t.to_dict() for t in self.tags]
        return d


@dataclass
class CreateObjectStorageReplicationResponse:
    detail: str = ""
    uuid: str = ""
    status: str = ""

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> CreateObjectStorageReplicationResponse:
        result: CreateObjectStorageReplicationResponse = _simple(cls, data)
        return result


@dataclass
class UpdateObjectStorageReplicationRequest:
    """Only the fields that are set are sent. ``enabled=False`` pauses, ``True`` resumes. To remove
    the prefix or the tag filter set ``clear_prefix`` or ``clear_tags`` (sends null). New
    credentials (access_key_id and secret_access_key, both) apply to external destinations only."""

    enabled: bool | None = None
    prefix: str | None = None
    clear_prefix: bool = False
    tags: list[ObjectStorageReplicationTag] | None = None
    clear_tags: bool = False
    delete_marker_replication: bool | None = None
    delete_replication: bool | None = None
    existing_objects: bool | None = None
    access_key_id: str | None = None
    secret_access_key: str | None = field(default=None, repr=False)

    def to_dict(self) -> dict[str, Any]:
        if self.prefix is not None and self.clear_prefix:
            raise ValueError("Set prefix or clear_prefix, not both")
        if self.tags is not None and self.clear_tags:
            raise ValueError("Set tags or clear_tags, not both")
        if (self.access_key_id is None) != (self.secret_access_key is None):
            raise ValueError("access_key_id and secret_access_key must be set together")
        d: dict[str, Any] = {}
        for k in ("enabled", "delete_marker_replication", "delete_replication", "existing_objects"):
            v = getattr(self, k)
            if v is not None:
                d[k] = v
        if self.clear_prefix:
            d["prefix"] = None
        elif self.prefix is not None:
            d["prefix"] = self.prefix
        if self.clear_tags:
            d["tags"] = None
        elif self.tags is not None:
            d["tags"] = [t.to_dict() for t in self.tags]
        if self.access_key_id is not None:
            d["destination"] = {"access_key_id": self.access_key_id, "secret_access_key": self.secret_access_key}
        return d


@dataclass
class ObjectStorageReplicationGrant:
    """Authorization for another organization to replicate into a bucket. status: open, used,
    expired or revoked. The token is never returned again after creation."""

    uuid: str = ""
    token_prefix: str = ""
    note: str | None = None
    status: str = ""
    expires_at: str | None = None
    used_at: str | None = None
    revoked_at: str | None = None
    created_at: str | None = None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> ObjectStorageReplicationGrant:
        result: ObjectStorageReplicationGrant = _simple(cls, data)
        return result


@dataclass
class CreateObjectStorageReplicationGrantRequest:
    note: str | None = None
    expires_in_days: int = 7
    """1 to 30."""

    def to_dict(self) -> dict[str, Any]:
        d: dict[str, Any] = {"expires_in_days": self.expires_in_days}
        if self.note is not None:
            d["note"] = self.note
        return d


@dataclass
class CreateObjectStorageReplicationGrantResponse:
    detail: str = ""
    uuid: str = ""
    token: str = field(default="", repr=False)
    """Returned only once: share it with the other organization now."""
    token_prefix: str = ""
    bucket_uuid: str = ""
    note: str | None = None
    expires_at: str = ""

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> CreateObjectStorageReplicationGrantResponse:
        result: CreateObjectStorageReplicationGrantResponse = _simple(cls, data)
        return result
