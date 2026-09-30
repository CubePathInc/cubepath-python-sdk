from __future__ import annotations

import json
from typing import Any

import httpx

from cubepath import CubePathClient
from cubepath.models import (
    CreateCDNOriginRequest,
    CreateObjectStorageAccessKeyRequest,
    CreateObjectStorageBucketRequest,
    UpdateObjectStorageBucketRequest,
)

TIER = {"uuid": "t1", "slug": "infrequent_access", "name": "Infrequent Access", "media": "hdd"}


def make_client(responses: dict[str, Any]) -> tuple[CubePathClient, list[httpx.Request]]:
    calls: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        calls.append(request)
        return httpx.Response(200, json=responses.get(f"{request.method} {request.url.path}", {}))

    client = CubePathClient(
        "test-token",
        base_url="https://api.test",
        http_client=httpx.Client(transport=httpx.MockTransport(handler)),
        rate_limit_interval=0,
    )
    return client, calls


def body(request: httpx.Request) -> Any:
    return json.loads(request.content)


def test_list_tiers() -> None:
    client, calls = make_client({"GET /object-storage/tiers": [{**TIER, "region": "eu", "accepting_new": True}]})
    tiers = client.object_storage.list_tiers()
    assert tiers[0].slug == "infrequent_access" and tiers[0].accepting_new is True
    assert str(calls[0].url) == "https://api.test/object-storage/tiers"


def test_bucket_lifecycle() -> None:
    bucket = {"uuid": "b1", "name": "photos", "status": "active", "tier": TIER, "cdn": None, "usage": None}
    client, calls = make_client(
        {
            "POST /object-storage/buckets": {"uuid": "b1", "name": "photos", "status": "pending", "tier": TIER},
            "GET /object-storage/buckets": [bucket],
            "GET /object-storage/buckets/b1": {**bucket, "connection": {"region": "eu"}},
        }
    )
    os = client.object_storage
    created = os.create_bucket(CreateObjectStorageBucketRequest(name="photos", tier="infrequent_access", project_id=12))
    assert created.status == "pending" and created.tier.slug == "infrequent_access"
    assert body(calls[0]) == {"name": "photos", "tier": "infrequent_access", "project_id": 12}

    listed = os.list_buckets(project_id=12, tier="infrequent_access")
    assert listed[0].tier.name == "Infrequent Access"
    assert calls[1].url.params == httpx.QueryParams({"project_id": "12", "tier": "infrequent_access"})

    detail = os.get_bucket("b1")
    assert detail.connection.region == "eu" and detail.cdn is None and detail.usage is None

    os.update_bucket("b1", UpdateObjectStorageBucketRequest(protected=True))
    assert calls[3].method == "PATCH" and body(calls[3]) == {"protected": True}

    os.delete_bucket("b1")
    os.delete_bucket("b1", force=True)
    assert [str(c.url) for c in calls[4:]] == [
        "https://api.test/object-storage/buckets/b1",
        "https://api.test/object-storage/buckets/b1?force=true",
    ]


def test_access_keys() -> None:
    key = {"uuid": "k1", "access_key_id": "CPX", "tier": TIER, "bucket_scope": [{"uuid": "b1", "name": "photos"}]}
    client, calls = make_client(
        {
            "POST /object-storage/keys": {**key, "secret_access_key": "secret"},
            "GET /object-storage/keys": [key, {**key, "uuid": "k2", "bucket_scope": None}],
        }
    )
    os = client.object_storage
    created = os.create_key(
        CreateObjectStorageAccessKeyRequest(
            name="web", tier="infrequent_access", permission="read_only", bucket_uuids=["b1"]
        )
    )
    assert created.secret_access_key == "secret" and created.bucket_scope is not None
    assert body(calls[0]) == {"name": "web", "tier": "infrequent_access", "permission": "read_only", "bucket_uuids": ["b1"]}
    keys = os.list_keys()
    assert keys[0].bucket_scope is not None and keys[0].bucket_scope[0].name == "photos"
    assert keys[1].bucket_scope is None
    os.delete_key("k1")
    assert calls[2].method == "DELETE" and calls[2].url.path == "/object-storage/keys/k1"


def test_usage() -> None:
    client, calls = make_client(
        {
            "GET /object-storage/usage": {
                "period": "2026-09",
                "tiers": [{"tier": TIER, "cost": 1.5, "free_tier": {"requests": {"included": 20000, "used": 10}}}],
                "buckets": [{"uuid": "b1", "cost": 1.5}],
                "available_months": ["2026-09"],
            }
        }
    )
    usage = client.object_storage.get_usage(period="2026-09")
    assert usage.tiers[0].free_tier["requests"].used == 10
    assert usage.buckets[0].cost == 1.5 and usage.available_months == ["2026-09"]
    assert calls[0].url.params == httpx.QueryParams({"period": "2026-09"})


def test_cdn_bucket_origin_sends_only_allowed_fields() -> None:
    client, calls = make_client({"POST /cdn/zones/z1/origins": {"uuid": "o1", "object_storage_bucket_uuid": "b1"}})
    origin = client.cdn.create_origin(
        "z1", CreateCDNOriginRequest(name="photos", weight=100, priority=1, object_storage_bucket_uuid="b1")
    )
    assert origin.object_storage_bucket_uuid == "b1"
    assert body(calls[0]) == {
        "name": "photos",
        "object_storage_bucket_uuid": "b1",
        "weight": 100,
        "priority": 1,
        "is_backup": False,
    }
