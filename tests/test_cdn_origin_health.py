from __future__ import annotations

import json

import httpx

from cubepath import CubePathClient
from cubepath.models import CreateCDNOriginRequest, UpdateCDNOriginRequest


def make_client(response: dict) -> tuple[CubePathClient, list[httpx.Request]]:
    calls: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        calls.append(request)
        return httpx.Response(200, json=response)

    client = CubePathClient(
        "test-token",
        base_url="https://api.test",
        http_client=httpx.Client(transport=httpx.MockTransport(handler)),
        rate_limit_interval=0,
    )
    return client, calls


def test_create_origin_sends_http_health_check_fields() -> None:
    client, calls = make_client(
        {
            "uuid": "o1",
            "health_check_type": "http",
            "health_check_method": "HEAD",
            "health_check_expected_status": "200",
            "health_check_interval": 15,
            "health_check_threshold": 2,
            "health_status": "unhealthy",
            "health_detail": "connection refused",
            "health_changed_at": "2026-11-25T10:00:00Z",
        }
    )
    origin = client.cdn.create_origin(
        "z1",
        CreateCDNOriginRequest(
            name="api",
            weight=100,
            priority=1,
            address="api.example.com",
            health_check_enabled=True,
            health_check_type="http",
            health_check_method="HEAD",
            health_check_expected_status="200",
            health_check_interval=15,
            health_check_threshold=2,
        ),
    )
    sent = json.loads(calls[0].content)
    assert sent["health_check_type"] == "http" and sent["health_check_method"] == "HEAD"
    assert sent["health_check_expected_status"] == "200"
    assert sent["health_check_interval"] == 15 and sent["health_check_threshold"] == 2
    assert "health_check_path" not in sent
    assert origin.health_check_interval == 15 and origin.health_detail == "connection refused"
    assert origin.health_changed_at == "2026-11-25T10:00:00Z"


def test_create_origin_omits_unset_health_check_fields() -> None:
    client, calls = make_client({"uuid": "o1"})
    client.cdn.create_origin("z1", CreateCDNOriginRequest(name="a", weight=100, priority=1, address="a.example.com"))
    sent = json.loads(calls[0].content)
    for key in (
        "health_check_type",
        "health_check_method",
        "health_check_expected_status",
        "health_check_interval",
        "health_check_threshold",
    ):
        assert key not in sent


def test_update_origin_health_check_fields_are_optional() -> None:
    client, calls = make_client({"uuid": "o1"})
    client.cdn.update_origin("z1", "o1", UpdateCDNOriginRequest(health_check_type="http", health_check_interval=30))
    assert json.loads(calls[0].content) == {"health_check_type": "http", "health_check_interval": 30}
