from __future__ import annotations

from typing import TYPE_CHECKING, Any

from cubepath.exceptions import APIError
from cubepath.models.object_storage import (
    CreateObjectStorageAccessKeyRequest,
    CreateObjectStorageAccessKeyResponse,
    CreateObjectStorageBucketRequest,
    CreateObjectStorageBucketResponse,
    ObjectStorageAccessKey,
    ObjectStorageBucket,
    ObjectStorageBucketDetail,
    ObjectStorageLifecycle,
    ObjectStorageLifecycleChange,
    ObjectStorageTier,
    ObjectStorageUsage,
    UpdateObjectStorageBucketRequest,
)

if TYPE_CHECKING:
    from cubepath.client import CubePathClient


def _filters(project_id: int | None, tier: str | None, period: str | None = None) -> dict[str, Any] | None:
    params: dict[str, Any] = {}
    if project_id is not None:
        params["project_id"] = project_id
    if tier:
        params["tier"] = tier
    if period:
        params["period"] = period
    return params or None


class ObjectStorageService:
    """S3 compatible Object Storage: tiers, buckets, access keys and usage."""

    def __init__(self, client: CubePathClient) -> None:
        self._client = client

    # ── Tiers ────────────────────────────────────────────────────

    def list_tiers(self) -> list[ObjectStorageTier]:
        data: list[dict[str, Any]] = self._client.get("/object-storage/tiers")
        return [ObjectStorageTier.from_dict(t) for t in data]

    # ── Buckets ──────────────────────────────────────────────────

    def list_buckets(self, *, project_id: int | None = None, tier: str | None = None) -> list[ObjectStorageBucket]:
        data: list[dict[str, Any]] = self._client.get("/object-storage/buckets", params=_filters(project_id, tier))
        return [ObjectStorageBucket.from_dict(b) for b in data]

    def get_bucket(self, uuid: str) -> ObjectStorageBucketDetail:
        data: dict[str, Any] = self._client.get(f"/object-storage/buckets/{uuid}")
        return ObjectStorageBucketDetail.from_dict(data)

    def create_bucket(self, req: CreateObjectStorageBucketRequest) -> CreateObjectStorageBucketResponse:
        """Create a bucket asynchronously: it is usable once its status is "active"."""
        data: dict[str, Any] = self._client.post("/object-storage/buckets", json=req.to_dict())
        return CreateObjectStorageBucketResponse.from_dict(data)

    def update_bucket(self, uuid: str, req: UpdateObjectStorageBucketRequest) -> None:
        self._client.patch(f"/object-storage/buckets/{uuid}", json=req.to_dict())

    def delete_bucket(self, uuid: str, *, force: bool = False) -> None:
        """Delete a bucket asynchronously. Without force only an empty bucket is deleted;
        with force every object and version is purged first."""
        self._client.delete(f"/object-storage/buckets/{uuid}", params={"force": "true"} if force else None)

    # ── Lifecycle rules ──────────────────────────────────────────

    def get_bucket_lifecycle(self, uuid: str) -> ObjectStorageLifecycle:
        data: dict[str, Any] = self._client.get(f"/object-storage/buckets/{uuid}/lifecycle")
        return ObjectStorageLifecycle.from_dict(data)

    def put_bucket_lifecycle(self, uuid: str, rules: list[dict[str, Any]]) -> ObjectStorageLifecycleChange:
        """Replace every lifecycle rule of the bucket (1 to 100). Expiration rules delete objects
        permanently. Applied asynchronously: poll get_bucket_lifecycle until .applied."""
        data: dict[str, Any] = self._client.put(f"/object-storage/buckets/{uuid}/lifecycle", json={"rules": rules})
        return ObjectStorageLifecycleChange.from_dict(data)

    def delete_bucket_lifecycle(self, uuid: str) -> ObjectStorageLifecycleChange:
        """Remove every lifecycle rule of the bucket."""
        data: dict[str, Any] = self._client.delete(f"/object-storage/buckets/{uuid}/lifecycle")
        return ObjectStorageLifecycleChange.from_dict(data or {})

    # ── Access keys ──────────────────────────────────────────────

    def list_keys(self, *, project_id: int | None = None, tier: str | None = None) -> list[ObjectStorageAccessKey]:
        data: list[dict[str, Any]] = self._client.get("/object-storage/keys", params=_filters(project_id, tier))
        return [ObjectStorageAccessKey.from_dict(k) for k in data]

    def create_key(self, req: CreateObjectStorageAccessKeyRequest) -> CreateObjectStorageAccessKeyResponse:
        """Create an access key. The secret is only returned here; the key works once its status is "active"."""
        data: dict[str, Any] = self._client.post("/object-storage/keys", json=req.to_dict())
        return CreateObjectStorageAccessKeyResponse.from_dict(data)

    def delete_key(self, uuid: str) -> None:
        self._client.delete(f"/object-storage/keys/{uuid}")

    # ── Usage ────────────────────────────────────────────────────

    def get_usage(
        self, *, period: str | None = None, project_id: int | None = None, tier: str | None = None
    ) -> ObjectStorageUsage:
        """Month usage and cost per tier and bucket. period is YYYY-MM, default the current month."""
        data: dict[str, Any] = self._client.get("/object-storage/usage", params=_filters(project_id, tier, period))
        return ObjectStorageUsage.from_dict(data)

    # ── Charts ───────────────────────────────────────────────────

    def get_bucket_metrics(self, uuid: str, time_range: str = "H24") -> dict[str, Any]:
        """Chart series of a bucket, served through GraphQL.

        ``time_range`` is H1, H3, H6, H12, H24, D3, D7 or D30. Returns ``{"uuid", "name",
        "storageMeasuredAt", "storage", "traffic", "responses"}``, each part a MetricsResult
        ``{"start", "end", "step", "series": [{"name", "unit", "points": [{"ts", "value"}]}]}``.
        storage: size_bytes, objects (hourly); traffic: egress_bytes, cdn_bytes, ingress_bytes,
        class_a_requests, class_b_requests, free_requests; responses: responses_2xx,
        responses_3xx, responses_4xx, responses_5xx, responses_429, responses_other. Traffic and
        responses are totals per step, not rates.
        """
        result = "start end step series { name unit points { ts value } }"
        data = self._client.graphql(
            "query($uuid: ID!, $range: TimeRange!) { objectStorageBucket(uuid: $uuid) { uuid name storageMeasuredAt "
            f"storage(range: $range) {{ {result} }} traffic(range: $range) {{ {result} }} "
            f"responses(range: $range) {{ {result} }} }} }}",
            {"uuid": uuid, "range": time_range},
        )
        if not data.get("objectStorageBucket"):
            raise APIError(404, "Not Found", f"Bucket {uuid} not found")
        bucket: dict[str, Any] = data["objectStorageBucket"]
        return bucket
