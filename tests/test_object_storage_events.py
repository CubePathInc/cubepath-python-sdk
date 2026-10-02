from __future__ import annotations

import json
from typing import Any

import httpx
import pytest

from cubepath import CubePathClient, StorageEventSignatureError, verify_storage_event_signature
from cubepath.models import (
    CreateObjectStorageEventDestinationRequest,
    CreateObjectStorageEventRuleRequest,
    UpdateObjectStorageEventDestinationRequest,
    UpdateObjectStorageEventRuleRequest,
)

SECRET = "whsec_0123456789abcdefABCDEF0123456789"
TS = "1790000000"
BODY = '{"id":"evt_01","type":"object.created"}'
SIG = "348e719a6c9fb75f1c6a60cc81ec5914a599eb648b1ab9d81e483fc2309c6f3b"
PREV_SIG = "d1cc88ad9e8ba98e234697ea257b0969a065c04f879a1c9cdcab90ef316a953d"
NOW = 1790000000.0

DEST = {"uuid": "d1", "name": "hook", "type": "webhook", "url_masked": "https://example.com/***", "status": "active"}


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


def test_event_routes() -> None:
    client, calls = make_client(
        {
            "POST /object-storage/event-destinations": {"destination": DEST, "signing_secret": "whsec_x"},
            "GET /object-storage/event-destinations": [DEST],
            "POST /object-storage/event-destinations/d1/rotate-secret": {
                "destination": DEST,
                "signing_secret": "whsec_y",
            },
            "GET /object-storage/event-destinations/d1/deliveries": {
                "deliveries": [
                    {"ts_ms": 1790964001250, "bucket_name": "photos", "status": "failed", "http_status": 500}
                ],
                "next_before": 1790964001250,
            },
            "POST /object-storage/buckets/b1/event-rules": {
                "uuid": "r1",
                "bucket_uuid": "b1",
                "destination": {"uuid": "d1"},
                "events": ["object.created"],
                "status": "pending",
            },
        }
    )
    os = client.object_storage
    created = os.create_event_destination(
        CreateObjectStorageEventDestinationRequest(name="hook", type="webhook", url="https://example.com/h")
    )
    assert created.signing_secret == "whsec_x" and created.destination.url_masked == "https://example.com/***"
    assert os.list_event_destinations()[0].uuid == "d1"
    os.get_event_destination("d1")
    os.update_event_destination("d1", UpdateObjectStorageEventDestinationRequest(enabled=False))
    assert os.rotate_event_destination_secret("d1").signing_secret == "whsec_y"
    os.test_event_destination("d1")
    page = os.list_event_deliveries("d1", status="failed", limit=10, before=1790964001251)
    assert page.next_before == 1790964001250 and page.deliveries[0].bucket_name == "photos"
    assert page.deliveries[0].http_status == 500 and page.deliveries[0].error == ""
    os.delete_event_destination("d1")
    os.list_event_rules("b1")
    rule = os.create_event_rule(
        "b1",
        CreateObjectStorageEventRuleRequest(name="r", destination_uuid="d1", events=["object.created"], prefix="in/"),
    )
    assert rule.status == "pending" and rule.destination["uuid"] == "d1"
    os.update_event_rule("b1", "r1", UpdateObjectStorageEventRuleRequest(enabled=False))
    os.delete_event_rule("b1", "r1")
    assert [f"{c.method} {c.url.path}" for c in calls] == [
        "POST /object-storage/event-destinations",
        "GET /object-storage/event-destinations",
        "GET /object-storage/event-destinations/d1",
        "PATCH /object-storage/event-destinations/d1",
        "POST /object-storage/event-destinations/d1/rotate-secret",
        "POST /object-storage/event-destinations/d1/test",
        "GET /object-storage/event-destinations/d1/deliveries",
        "DELETE /object-storage/event-destinations/d1",
        "GET /object-storage/buckets/b1/event-rules",
        "POST /object-storage/buckets/b1/event-rules",
        "PATCH /object-storage/buckets/b1/event-rules/r1",
        "DELETE /object-storage/buckets/b1/event-rules/r1",
    ]
    assert json.loads(calls[0].content) == {"name": "hook", "type": "webhook", "url": "https://example.com/h"}
    assert json.loads(calls[3].content) == {"enabled": False}
    assert calls[6].url.params == httpx.QueryParams({"status": "failed", "limit": "10", "before": "1790964001251"})
    assert json.loads(calls[9].content) == {
        "name": "r",
        "destination_uuid": "d1",
        "events": ["object.created"],
        "enabled": True,
        "prefix": "in/",
    }


@pytest.mark.parametrize(
    "secret,body,header",
    [
        (SECRET, BODY, f"v1={SIG}"),
        (SECRET, BODY.encode(), f"v1={PREV_SIG},v1={SIG}"),
        ("whsec_previous", BODY, f"v1={SIG}, v1={PREV_SIG}"),
        # The exact form the service sends during a rotation.
        (SECRET, BODY, f"v1={SIG}, v1={PREV_SIG}"),
    ],
)
def test_signature_valid(secret: str, body: Any, header: str) -> None:
    verify_storage_event_signature(secret, TS, body, header, now=NOW)


@pytest.mark.parametrize(
    "ts,body,header,now",
    [
        (TS, '{"id":"evt_02"}', f"v1={SIG}", NOW),
        (TS, BODY, f"v1={PREV_SIG}", NOW),
        (TS, BODY, f"v0={SIG}", NOW),
        (TS, BODY, f"v1={SIG}", NOW + 360),
        (TS, BODY, f"v1={SIG}", NOW - 360),
        ("abc", BODY, f"v1={SIG}", NOW),
        (TS, BODY, "", NOW),
        (TS, BODY, "v1=abcd", NOW),
    ],
)
def test_signature_rejected(ts: str, body: str, header: str, now: float) -> None:
    with pytest.raises(StorageEventSignatureError):
        verify_storage_event_signature(SECRET, ts, body, header, now=now)


def test_signature_tolerance() -> None:
    verify_storage_event_signature(SECRET, TS, BODY, f"v1={SIG}", 0, now=NOW + 3600)
    with pytest.raises(StorageEventSignatureError):
        verify_storage_event_signature(SECRET, TS, BODY, f"v1={SIG}")
