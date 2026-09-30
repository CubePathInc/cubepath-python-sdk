from __future__ import annotations

import json
from typing import Any

import httpx
import pytest

from cubepath import CubePathClient
from cubepath.exceptions import APIError
from cubepath.models import CreateFirewallGroupRequest, UpdateFirewallGroupRequest, VPSFirewallGroupsRequest


def make_client(responses: dict[str, Any]) -> tuple[CubePathClient, list[httpx.Request]]:
    calls: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        calls.append(request)
        key = f"{request.method} {request.url.path}"
        value = responses.get(key, {})
        if isinstance(value, list) and value and isinstance(value[0], tuple):
            value = value.pop(0)[1]
        return httpx.Response(200, json=value)

    client = CubePathClient(
        "test-token",
        base_url="https://api.test",
        http_client=httpx.Client(transport=httpx.MockTransport(handler)),
        rate_limit_interval=0,
        max_retries=0,
    )
    return client, calls


def body(request: httpx.Request) -> Any:
    return json.loads(request.content)


def test_assign_to_vps_uses_firewall_route() -> None:
    client, calls = make_client(
        {"PUT /firewall/vps/7/groups": {"detail": "ok", "vps_id": 7, "firewall_groups": [3], "sync_task_created": True}}
    )
    res = client.firewall.assign_to_vps("7", VPSFirewallGroupsRequest(firewall_group_ids=["3"]))
    assert calls[0].method == "PUT" and calls[0].url.path == "/firewall/vps/7/groups"
    assert body(calls[0]) == {"firewall_group_ids": ["3"]}
    assert res.detail == "ok" and res.sync_task_created


def test_create_firewall_group_sends_project_id_in_query() -> None:
    client, calls = make_client({"POST /firewall/groups": {"id": 5, "name": "web"}})
    client.firewall.create(CreateFirewallGroupRequest(name="web", project_id=12))
    assert calls[0].url.params["project_id"] == "12"
    assert "project_id" not in body(calls[0])
    with pytest.raises(ValueError):
        client.firewall.create(CreateFirewallGroupRequest(name="web"))


def test_firewall_update_uses_put_and_get_uses_list() -> None:
    client, calls = make_client(
        {
            "PUT /firewall/groups/5": {"id": 5, "name": "new"},
            "GET /firewall/groups": [{"id": 4, "name": "a"}, {"id": 5, "name": "b"}],
        }
    )
    client.firewall.update("5", UpdateFirewallGroupRequest(name="new"))
    group = client.firewall.get("5")
    assert calls[0].method == "PUT"
    assert calls[1].url.path == "/firewall/groups" and group.name == "b"
    with pytest.raises(APIError) as exc:
        client.firewall.get("99")
    assert exc.value.is_not_found()


def test_load_balancer_get_uses_list() -> None:
    client, calls = make_client({"GET /loadbalancer/": [{"uuid": "a", "name": "x"}, {"uuid": "b", "name": "y"}]})
    assert client.load_balancer.get("b").name == "y"
    assert calls[0].url.path == "/loadbalancer/"


def test_nat_metrics_and_bandwidth_via_graphql() -> None:
    client, calls = make_client(
        {
            "POST /graphql": [
                ("m", {"data": {"natGateway": {"metrics": {"start": 1, "end": 2, "step": 30, "series": []}}}}),
                (
                    "b",
                    {
                        "data": {
                            "natGateway": {
                                "bandwidthUsage": {
                                    "inBytes": 1,
                                    "outBytes": 2,
                                    "totalBytes": 3,
                                    "periodStart": 0,
                                    "periodEnd": 1,
                                }
                            }
                        }
                    },
                ),
            ]
        }
    )
    metrics = client.nat_gateway.get_metrics("u1", "H24")
    usage = client.nat_gateway.get_bandwidth_usage("u1")
    assert body(calls[0])["variables"] == {"uuid": "u1", "range": "H24"}
    assert metrics["step"] == 30 and usage["totalBytes"] == 3


def test_graphql_not_found_is_404() -> None:
    client, _ = make_client(
        {
            "POST /graphql": {
                "data": {"natGateway": None},
                "errors": [{"message": "Resource not found.", "extensions": {"code": "NOT_FOUND"}}],
            }
        }
    )
    with pytest.raises(APIError) as exc:
        client.nat_gateway.get_metrics("nope")
    assert exc.value.is_not_found()


def test_bmc_sensors_via_graphql() -> None:
    client, calls = make_client(
        {
            "POST /graphql": {
                "data": {
                    "baremetal": {
                        "sensors": {
                            "ipmiAvailable": True,
                            "powerOn": True,
                            "lastSeen": 100,
                            "temperatures": [{"name": "CPU", "value": 41.5, "unit": "CELSIUS"}],
                            "fans": [],
                        }
                    }
                }
            }
        }
    )
    sensors = client.baremetal.bmc_sensors("9")
    assert body(calls[0])["variables"] == {"id": "9"}
    assert sensors.ipmi_available and sensors.last_seen == 100
    assert sensors.sensors["temperatures"][0].unit == "CELSIUS"
    assert sensors.sensors["temperatures"][0].value == 41.5


def test_reinstall_status_cancel_and_monitoring() -> None:
    client, calls = make_client(
        {"GET /projects/": [{"project": {"id": 1}, "baremetals": [{"id": 9, "status": "deploying"}]}]}
    )
    status = client.baremetal.reinstall_status("9")
    client.baremetal.cancel_reinstall("9")
    client.baremetal.monitoring_enable("9")
    assert status.is_reinstalling and status.status == "deploying"
    assert calls[1].method == "DELETE" and calls[1].url.path == "/baremetal/9/reinstall"
    assert calls[2].method == "PUT" and calls[2].url.params["enable"] == "true" and not calls[2].content
