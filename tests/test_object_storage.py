from __future__ import annotations

import json
from typing import Any

import httpx
import pytest

from cubepath import CubePathClient
from cubepath.models import (
    CreateCDNOriginRequest,
    CreateObjectStorageAccessKeyRequest,
    CreateObjectStorageBucketRequest,
    CreateObjectStorageReplicationGrantRequest,
    CreateObjectStorageReplicationRequest,
    ObjectStorageLockRetention,
    ObjectStorageReplicationDestinationRequest,
    ObjectStorageReplicationTag,
    SetObjectStorageObjectLockRequest,
    UpdateObjectStorageBucketRequest,
    UpdateObjectStorageReplicationRequest,
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
    assert body(calls[0]) == {
        "name": "web",
        "tier": "infrequent_access",
        "permission": "read_only",
        "bucket_uuids": ["b1"],
    }
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


def test_bucket_lifecycle_rules() -> None:
    path = "/object-storage/buckets/b1/lifecycle"
    client, calls = make_client(
        {
            f"GET {path}": {
                "bucket_uuid": "b1",
                "status": "pending",
                "generation": 4,
                "applied_generation": 3,
                "rules": [{"id": "logs-30d", "enabled": True, "expiration": {"days": 30}}],
                "notes": ["n"],
            },
            f"PUT {path}": {"detail": "Lifecycle rules are being applied", "generation": 5, "notes": []},
            f"DELETE {path}": {"detail": "This bucket has no lifecycle rules"},
        }
    )
    lifecycle = client.object_storage.get_bucket_lifecycle("b1")
    assert not lifecycle.applied
    assert lifecycle.rules[0]["id"] == "logs-30d"
    rules = [{"id": "logs-30d", "enabled": True, "filter": {"prefix": "logs/"}, "expiration": {"days": 30}}]
    change = client.object_storage.put_bucket_lifecycle("b1", rules)
    assert change.generation == 5
    assert calls[1].method == "PUT" and body(calls[1]) == {"rules": rules}
    change = client.object_storage.delete_bucket_lifecycle("b1")
    assert change.generation is None and calls[2].method == "DELETE" and calls[2].url.path == path


def test_bucket_metrics_through_graphql() -> None:
    part = {"start": 1, "end": 2, "step": 300, "series": []}
    bucket = {"uuid": "b1", "name": "photos", "storageMeasuredAt": 1}
    bucket.update({"storage": part, "traffic": part, "responses": part})
    client, calls = make_client({"POST /graphql": {"data": {"objectStorageBucket": bucket}}})
    assert client.object_storage.get_bucket_metrics("b1", "D7") == bucket
    sent = body(calls[0])
    assert sent["variables"] == {"uuid": "b1", "range": "D7"}
    assert "objectStorageBucket(uuid: $uuid)" in sent["query"]
    assert "responses(range: $range) { start end step series" in sent["query"]


def test_bucket_metrics_not_found() -> None:
    from cubepath.exceptions import APIError

    errors = [{"message": "Resource not found.", "extensions": {"code": "NOT_FOUND"}}]
    client, _ = make_client({"POST /graphql": {"data": {"objectStorageBucket": None}, "errors": errors}})
    try:
        client.object_storage.get_bucket_metrics("nope")
    except APIError as exc:
        assert exc.status_code == 404
    else:
        raise AssertionError("expected APIError")


def test_object_lock() -> None:
    lock = {"enabled": True, "default_retention": {"mode": "governance", "days": 30, "years": None}}
    client, calls = make_client(
        {
            "POST /object-storage/buckets": {"uuid": "b1", "status": "pending", "tier": TIER, "object_lock": lock},
            "GET /object-storage/buckets": [
                {"uuid": "b1", "tier": TIER, "object_lock": lock, "locked_content_kept": True},
                {"uuid": "b2", "tier": TIER, "object_lock": {"enabled": False, "default_retention": None}},
            ],
            "GET /object-storage/buckets/b1": {"uuid": "b1", "tier": TIER, "object_lock": lock},
        }
    )
    os = client.object_storage
    created = os.create_bucket(
        CreateObjectStorageBucketRequest(
            name="vault",
            tier="infrequent_access",
            object_lock=True,
            object_lock_default=ObjectStorageLockRetention(mode="governance", days=30),
            accept_object_lock_terms=True,
        )
    )
    assert body(calls[0]) == {
        "name": "vault",
        "tier": "infrequent_access",
        "versioning": True,
        "object_lock": True,
        "object_lock_default": {"mode": "governance", "days": 30},
        "accept_object_lock_terms": True,
    }
    assert created.object_lock.enabled and created.object_lock.default_retention is not None
    assert created.object_lock.default_retention.days == 30

    listed = os.list_buckets()
    assert listed[0].locked_content_kept is True and listed[0].object_lock.enabled is True
    assert listed[1].object_lock.default_retention is None and listed[1].locked_content_kept is False
    detail = os.get_bucket("b1")
    rule = detail.object_lock.default_retention
    assert rule is not None and rule.mode == "governance"

    os.set_bucket_object_lock(
        "b1",
        SetObjectStorageObjectLockRequest(
            default_retention=ObjectStorageLockRetention(mode="compliance", years=1), accept_object_lock_terms=True
        ),
    )
    assert calls[3].method == "PUT" and calls[3].url.path == "/object-storage/buckets/b1/object-lock"
    assert body(calls[3]) == {"default_retention": {"mode": "compliance", "years": 1}, "accept_object_lock_terms": True}
    os.set_bucket_object_lock("b1", SetObjectStorageObjectLockRequest())
    assert body(calls[4]) == {"default_retention": None, "accept_object_lock_terms": False}

    os.delete_bucket("b1", force=True, bypass_governance=True)
    assert calls[5].url.params == httpx.QueryParams({"force": "true", "bypass_governance": "true"})


def test_access_key_bypass_governance() -> None:
    client, calls = make_client({"POST /object-storage/keys": {"uuid": "k1", "tier": TIER, "bypass_governance": True}})
    created = client.object_storage.create_key(
        CreateObjectStorageAccessKeyRequest(name="veeam", tier="infrequent_access", bypass_governance=True)
    )
    assert created.bypass_governance is True
    assert body(calls[0]) == {
        "name": "veeam",
        "tier": "infrequent_access",
        "permission": "read_write",
        "bypass_governance": True,
    }


def test_bucket_encryption() -> None:
    client, _calls = make_client(
        {
            "GET /object-storage/buckets": [
                {"uuid": "b1", "tier": TIER, "encryption": {"algorithm": "AES256", "scope": "new_objects"}},
                {"uuid": "b2", "tier": TIER, "encryption": None},
            ],
            "GET /object-storage/buckets/b1": {
                "uuid": "b1",
                "tier": TIER,
                "encryption": {"algorithm": "AES256", "scope": "all_objects"},
            },
        }
    )
    buckets = client.object_storage.list_buckets()
    assert buckets[0].encryption is not None
    assert (buckets[0].encryption.algorithm, buckets[0].encryption.scope) == ("AES256", "new_objects")
    assert buckets[1].encryption is None
    # the detail parses it too (it was left as a raw dict)
    detail = client.object_storage.get_bucket("b1")
    assert detail.encryption is not None
    assert (detail.encryption.algorithm, detail.encryption.scope) == ("AES256", "all_objects")


REPLICATION = {
    "uuid": "r1",
    "status": "active",
    "pause_reason": None,
    "direction": "outgoing",
    "source": {"bucket_uuid": "b1", "bucket_name": "photos", "project_id": 12, "same_organization": True},
    "destination": {
        "type": "external",
        "provider": "aws",
        "endpoint": "s3.eu-west-1.amazonaws.com",
        "region": "eu-west-1",
        "bucket": "acme-backup",
        "path_style": "auto",
        "access_key_id": "****WXYZ",
    },
    "rules": {
        "enabled": True,
        "prefix": None,
        "tags": [{"key": "backup", "value": "yes"}],
        "delete_marker_replication": False,
        "delete_replication": False,
        "existing_objects": True,
    },
    "health": "ok",
    "backfill": {"status": "completed", "objects": 3, "bytes": 30, "failed_objects": 0},
    "created_at": "2026-10-02T08:59:30",
}


def test_replication_list_and_get() -> None:
    client, calls = make_client(
        {
            "GET /object-storage/replications": [REPLICATION],
            "GET /object-storage/replications/r1": {
                **REPLICATION,
                "metrics": {"replicated_bytes_24h": 100, "queued_objects": 0, "egress_bytes_month": 500},
            },
        }
    )
    os = client.object_storage
    listed = os.list_replications(direction="outgoing", bucket_uuid="b1")
    assert calls[0].url.params == httpx.QueryParams({"direction": "outgoing", "bucket_uuid": "b1"})
    r = listed[0]
    assert r.source.bucket_name == "photos" and r.destination.type == "external"
    assert r.destination.access_key_id == "****WXYZ" and r.destination.bucket == "acme-backup"
    assert r.rules.tags[0].key == "backup" and r.rules.existing_objects is True
    assert r.backfill.status == "completed" and r.backfill.bytes == 30 and r.health == "ok"

    os.list_replications()
    assert str(calls[1].url) == "https://api.test/object-storage/replications"

    detail = os.get_replication("r1")
    assert detail.metrics is not None and detail.metrics.egress_bytes_month == 500
    assert detail.destination.region == "eu-west-1"


def test_replication_get_without_metrics() -> None:
    incoming = {
        **REPLICATION,
        "direction": "incoming",
        "source": {
            "bucket_uuid": None,
            "bucket_name": "photos",
            "organization_name": "Acme",
            "same_organization": False,
        },
        "destination": {"type": "cubepath", "bucket_uuid": "b9", "bucket_name": "copy", "same_organization": False},
        "metrics": None,
    }
    client, _ = make_client({"GET /object-storage/replications/r1": incoming})
    detail = client.object_storage.get_replication("r1")
    assert detail.metrics is None and detail.source.bucket_uuid is None
    assert detail.destination.type == "cubepath" and detail.destination.bucket_name == "copy"


def test_create_replication_cubepath_and_external() -> None:
    client, calls = make_client(
        {
            "POST /object-storage/replications": {
                "detail": "Replication is being configured",
                "uuid": "r1",
                "status": "pending",
            }
        }
    )
    os = client.object_storage
    created = os.create_replication(
        CreateObjectStorageReplicationRequest(
            source_bucket_uuid="b1",
            destination=ObjectStorageReplicationDestinationRequest.cubepath("b2", grant_token="cprg_x"),
            prefix="img/",
        )
    )
    assert created.uuid == "r1" and created.status == "pending"
    assert body(calls[0]) == {
        "source_bucket_uuid": "b1",
        "destination": {"type": "cubepath", "bucket_uuid": "b2", "grant_token": "cprg_x"},
        "prefix": "img/",
        "delete_marker_replication": False,
        "delete_replication": False,
        "existing_objects": True,
    }

    dest = ObjectStorageReplicationDestinationRequest.external(
        endpoint="s3.eu-west-1.amazonaws.com",
        region="eu-west-1",
        bucket="acme-backup",
        access_key_id="AKIA",
        secret_access_key="s3cr3t",
        provider="aws",
    )
    assert "s3cr3t" not in repr(dest)
    os.create_replication(
        CreateObjectStorageReplicationRequest(
            source_bucket_uuid="b1",
            destination=dest,
            tags=[ObjectStorageReplicationTag(key="backup", value="yes")],
            existing_objects=False,
        )
    )
    sent = body(calls[1])
    assert sent["destination"] == {
        "type": "external",
        "provider": "aws",
        "endpoint": "s3.eu-west-1.amazonaws.com",
        "region": "eu-west-1",
        "bucket": "acme-backup",
        "access_key_id": "AKIA",
        "secret_access_key": "s3cr3t",
    }
    assert sent["tags"] == [{"key": "backup", "value": "yes"}] and sent["existing_objects"] is False
    assert "prefix" not in sent


def test_update_replication() -> None:
    client, calls = make_client({})
    os = client.object_storage
    os.update_replication("r1", UpdateObjectStorageReplicationRequest(enabled=False))
    assert calls[0].method == "PATCH" and calls[0].url.path == "/object-storage/replications/r1"
    assert body(calls[0]) == {"enabled": False}

    os.update_replication("r1", UpdateObjectStorageReplicationRequest(clear_prefix=True, clear_tags=True))
    assert body(calls[1]) == {"prefix": None, "tags": None}

    os.update_replication(
        "r1", UpdateObjectStorageReplicationRequest(prefix="logs/", access_key_id="AKIA2", secret_access_key="new")
    )
    assert body(calls[2]) == {"prefix": "logs/", "destination": {"access_key_id": "AKIA2", "secret_access_key": "new"}}

    with pytest.raises(ValueError):
        UpdateObjectStorageReplicationRequest(prefix="a/", clear_prefix=True).to_dict()
    with pytest.raises(ValueError):
        UpdateObjectStorageReplicationRequest(access_key_id="AKIA").to_dict()


def test_replication_delete_resync_revoke() -> None:
    client, calls = make_client({})
    os = client.object_storage
    os.delete_replication("r1")
    os.resync_replication("r1", older_than_days=3)
    os.resync_replication("r1")
    os.revoke_replication("r1")
    assert [(c.method, c.url.path) for c in calls] == [
        ("DELETE", "/object-storage/replications/r1"),
        ("POST", "/object-storage/replications/r1/resync"),
        ("POST", "/object-storage/replications/r1/resync"),
        ("POST", "/object-storage/replications/r1/revoke"),
    ]
    assert body(calls[1]) == {"older_than_days": 3}
    assert body(calls[2]) == {"older_than_days": None}


def test_replication_grants() -> None:
    client, calls = make_client(
        {
            "POST /object-storage/buckets/b2/replication-grants": {
                "detail": "Replication grant created",
                "uuid": "g1",
                "token": "cprg_AbCdEfGhIjKlMnOpQrStUvWxYz012345",
                "token_prefix": "cprg_AbCd",
                "bucket_uuid": "b2",
                "note": "for Acme",
                "expires_at": "2026-10-09T10:00:00",
            },
            "GET /object-storage/buckets/b2/replication-grants": [
                {"uuid": "g1", "token_prefix": "cprg_AbCd", "status": "open", "expires_at": "2026-10-09T10:00:00"}
            ],
        }
    )
    os = client.object_storage
    grant = os.create_replication_grant(
        "b2", CreateObjectStorageReplicationGrantRequest(note="for Acme", expires_in_days=3)
    )
    assert grant.token.startswith("cprg_") and grant.token not in repr(grant)
    assert body(calls[0]) == {"note": "for Acme", "expires_in_days": 3}

    os.create_replication_grant("b2")
    assert body(calls[1]) == {"expires_in_days": 7}

    grants = os.list_replication_grants("b2")
    assert grants[0].status == "open" and grants[0].token_prefix == "cprg_AbCd"

    os.delete_replication_grant("g1")
    assert calls[3].method == "DELETE" and calls[3].url.path == "/object-storage/replication-grants/g1"
