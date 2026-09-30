from __future__ import annotations

import json
from typing import Any

import httpx
import pytest

from cubepath import CubePathClient
from cubepath.models import (
    AlertActionRequest,
    CreateAlertRequest,
    CreateDDoSFirewallRuleRequest,
    CreateManagedDatabaseRequest,
    CreateManagedDatabaseUserRequest,
    CreateNotificatorRequest,
    CreateTranscoderBatchRequest,
    CreateTranscoderJobRequest,
    DDoSTrafficCaptureRequest,
    DDoSTrafficStatsRequest,
    ManagedDatabaseBackupConfig,
    ManagedDatabaseBackupPolicyUpdate,
    TranscoderBatchInput,
    TranscoderJobInput,
    TranscoderJobOutput,
    TranscoderOutputSpec,
    TranscoderS3Config,
    UpdateAlertRequest,
    UpdateDDoSProtectionProfileRequest,
    UpdateManagedDatabaseRequest,
    UpdateNotificatorRequest,
)


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
        max_retries=0,
    )
    return client, calls


def body(request: httpx.Request) -> Any:
    return json.loads(request.content)


# ── Managed databases ────────────────────────────────────────────

PLAN = {
    "uuid": "p1",
    "name": "valkey.micro",
    "engine": "valkey",
    "cpu": 2,
    "memory_gb": 4,
    "storage_gb": 60,
    "max_replicas": 5,
    "price_per_hour": 0.02778,
}


def test_managed_database_lifecycle() -> None:
    detail = {
        "uuid": "m1",
        "project_id": 7,
        "name": "cache",
        "engine": "valkey",
        "version": "7.2.11",
        "topology": "replication",
        "replicas": 2,
        "status": "active",
        "endpoint_host": "203.0.113.5",
        "endpoint_port": 6379,
        "plan": PLAN,
        "location": {"id": 1, "location_name": "eu-bcn-1", "description": "Barcelona"},
        "backup_enabled": False,
        "billing_type": "hourly",
        "protected": False,
        "updated_at": "2026-09-30T10:00:00",
    }
    client, calls = make_client(
        {
            "GET /managed-database-plans/": [{"location_name": "eu-bcn-1", "plans": [PLAN]}],
            "POST /managed-databases/": {"uuid": "m1", "name": "cache", "status": "provisioning"},
            "GET /managed-databases/": [{k: v for k, v in detail.items() if k not in ("plan", "location")}],
            "GET /managed-databases/m1": detail,
        }
    )
    md = client.managed_databases
    plans = md.list_plans(engine="valkey")
    assert plans[0].plans[0].price_per_hour == 0.02778
    assert calls[0].url.params["engine"] == "valkey"

    created = md.create(
        CreateManagedDatabaseRequest(
            project_id=7,
            name="cache",
            engine="valkey",
            version="7.2.11",
            plan_uuid="p1",
            replicas=2,
            backup=ManagedDatabaseBackupConfig(schedule_cron="0 3 * * *"),
        )
    )
    assert created.status == "provisioning"
    assert body(calls[1]) == {
        "project_id": 7,
        "name": "cache",
        "engine": "valkey",
        "version": "7.2.11",
        "plan_uuid": "p1",
        "replicas": 2,
        "backup": {"schedule_cron": "0 3 * * *", "retention_days": 7},
    }
    assert md.list()[0].endpoint_port == 6379
    got = md.get("m1")
    assert got.plan.name == "valkey.micro" and got.location.location_name == "eu-bcn-1"

    md.update("m1", UpdateManagedDatabaseRequest(label="prod", backup=ManagedDatabaseBackupPolicyUpdate(enabled=False)))
    assert calls[4].method == "PATCH" and body(calls[4]) == {"label": "prod", "backup": {"enabled": False}}
    md.configure_protection("m1", True)
    assert calls[5].url.path == "/managed-databases/m1/protection" and body(calls[5]) == {"enabled": True}
    md.delete("m1")
    assert calls[6].method == "DELETE" and calls[6].url.path == "/managed-databases/m1"


def test_managed_database_operations() -> None:
    client, calls = make_client(
        {
            "POST /managed-databases/m1/scale": {"detail": "ok", "uuid": "m1", "replicas": 3},
            "GET /managed-databases/m1/credentials": {
                "host": "h",
                "port": 6379,
                "username": "cubeadmin",
                "password": "pw",
                "uri": "redis://cubeadmin:pw@h:6379",
            },
            "GET /managed-databases/m1/config": {
                "engine": "valkey",
                "params": {"maxmemory-policy": {"type": "enum", "value": "noeviction", "enum": ["noeviction"]}},
                "note": "",
            },
            "PATCH /managed-databases/m1/config": {"detail": "ok", "uuid": "m1", "requires_restart": []},
            "GET /managed-databases/m1/metrics": {"start": 1, "end": 2, "metrics": {"cpu": [[1, 0.5]]}},
        }
    )
    md = client.managed_databases
    assert md.scale("m1", replicas=3).replicas == 3
    assert body(calls[0]) == {"replicas": 3}
    with pytest.raises(ValueError):
        md.scale("m1")
    with pytest.raises(ValueError):
        md.scale("m1", replicas=3, plan_uuid="p2")
    assert md.get_credentials("m1").uri.startswith("redis://")
    md.rotate_credentials("m1")
    assert calls[2].method == "POST" and calls[2].url.path == "/managed-databases/m1/credentials/rotate"
    assert md.get_config("m1").params["maxmemory-policy"].enum == ["noeviction"]
    md.update_config("m1", {"maxmemory-policy": "noeviction"})
    assert body(calls[4]) == {"params": {"maxmemory-policy": "noeviction"}}
    metrics = md.get_metrics("m1", metrics=["cpu", "memory"], time_range="24h")
    assert metrics.metrics["cpu"] == [[1, 0.5]]
    assert calls[5].url.params == httpx.QueryParams({"metrics": "cpu,memory", "time_range": "24h"})


def test_managed_database_objects() -> None:
    client, calls = make_client(
        {
            "GET /managed-databases/m1/databases": [{"uuid": "d1", "name": "app", "status": "active"}],
            "POST /managed-databases/m1/databases": {"detail": "ok", "uuid": "d2", "name": "logs", "status": "pending"},
            "GET /managed-databases/m1/users": [{"uuid": "u1", "username": "app", "status": "active"}],
            "POST /managed-databases/m1/users": {
                "uuid": "u2",
                "username": "ro",
                "password": "generated",
                "status": "pending",
            },
        }
    )
    md = client.managed_databases
    assert md.list_databases("m1")[0].name == "app"
    assert md.create_database("m1", "logs").uuid == "d2"
    assert body(calls[1]) == {"name": "logs"}
    md.delete_database("m1", "d2")
    assert calls[2].method == "DELETE" and calls[2].url.path == "/managed-databases/m1/databases/d2"
    assert md.list_users("m1")[0].username == "app"
    user = md.create_user("m1", CreateManagedDatabaseUserRequest(username="ro"))
    assert user.password == "generated" and body(calls[4]) == {"username": "ro"}
    md.delete_user("m1", "u2")
    assert calls[5].url.path == "/managed-databases/m1/users/u2"


# ── DDoS mitigation ──────────────────────────────────────────────


def test_ddos_attacks_no_attacks_detail() -> None:
    client, _ = make_client({"GET /ddos-attacks/attacks": {"detail": "No recent DDoS attacks were found."}})
    assert client.ddos.list_attacks() == []
    client, calls = make_client({"GET /ddos-attacks/attacks": [{"attack_id": 4, "gbps_peak": 9.4}]})
    assert client.ddos.list_attacks()[0].gbps_peak == 9.4
    client.ddos.get_attack_details(4)
    client.ddos.get_attack_traffic_graph(4)
    assert [c.url.path for c in calls[1:]] == [
        "/ddos-attacks/attacks/4/details",
        "/ddos-attacks/attacks/4/traffic-graph",
    ]


def test_ddos_ips_and_profiles() -> None:
    client, calls = make_client(
        {
            "GET /ddos-mitigation/ips": {
                "single_ips": [{"network": "203.0.113.5", "protection_type": "Premium"}],
                "subnets": [{"network": "198.51.100.0", "prefix": 29, "ip_addresses": [{"address": "198.51.100.1"}]}],
                "total": 2,
            },
            "GET /ddos-mitigation/profiles/198.51.100.0/29": {"network": "198.51.100.0/29", "udp_threshold_pps": 500},
            "GET /ddos-mitigation/profiles/203.0.113.5/countries": {"countries": [{"iso_code": "ES"}], "total": 1},
        }
    )
    d = client.ddos_mitigation
    ips = d.list_ips(has_profile=True)
    assert ips.subnets[0].ip_addresses[0].address == "198.51.100.1"
    assert calls[0].url.params["has_profile"] == "true"

    profile = d.get_profile("198.51.100.0/29")
    assert calls[1].url.path == "/ddos-mitigation/profiles/198.51.100.0/29"
    req = profile.to_request()
    req.udp_threshold_pps = 800
    d.update_profile("198.51.100.0/29", req)
    sent = body(calls[2])
    assert calls[2].method == "PUT" and sent["udp_threshold_pps"] == 800 and "network" not in sent
    assert "always_on_mitigation" not in sent and sent["tcp_syn_threshold_pps"] == 10

    full = UpdateDDoSProtectionProfileRequest(symmetric_routing=1).to_dict()
    assert full["symmetric_routing"] == 1 and len(full) == 27

    assert d.get_profile_countries("203.0.113.5")[0].iso_code == "ES"
    d.set_profile_countries("203.0.113.5", ["ES", "FR"])
    d.set_profile_asns("203.0.113.5", [13335])
    d.set_profile_prefix_lists("203.0.113.5", ["pl1"])
    assert [body(c) for c in calls[4:7]] == [{"iso_codes": ["ES", "FR"]}, {"asns": [13335]}, {"uuids": ["pl1"]}]
    d.delete_profile("203.0.113.5")
    assert calls[7].method == "DELETE"


def test_ddos_prefix_lists_and_firewall() -> None:
    client, calls = make_client(
        {
            "GET /ddos-mitigation/prefix-lists": {"prefix_lists": [{"uuid": "pl1", "name": "office"}], "total": 1},
            "GET /ddos-mitigation/prefix-lists/pl1/entries": [{"network": "192.0.2.0/24"}],
            "GET /ddos-mitigation/firewall-rules/203.0.113.5": {
                "rules": [{"id": 9, "action_label": "DROP"}],
                "total": 1,
            },
            "GET /ddos-mitigation/asns": {"asns": [{"asn": 13335, "name": "CLOUDFLARENET"}], "total": 1},
        }
    )
    d = client.ddos_mitigation
    d.create_prefix_list("office", "HQ")
    assert body(calls[0]) == {"name": "office", "description": "HQ"}
    assert d.list_prefix_lists()[0].uuid == "pl1"
    d.add_prefix_list_entry("pl1", "192.0.2.0/24")
    assert d.list_prefix_list_entries("pl1") == ["192.0.2.0/24"]
    d.delete_prefix_list_entry("pl1", "192.0.2.0/24")
    assert calls[4].url.path == "/ddos-mitigation/prefix-lists/pl1/entries/192.0.2.0/24"
    d.delete_prefix_list("pl1")

    d.create_firewall_rule(
        CreateDDoSFirewallRuleRequest(network="203.0.113.5", protocol=17, dst_port=0, action=60, udp=1000)
    )
    sent = body(calls[6])
    assert sent["action"] == 60 and sent["udp"] == 1000 and sent["tcp_syn"] == 0
    assert d.list_firewall_rules("203.0.113.5")[0].id == 9
    d.delete_firewall_rule(9)
    d.delete_firewall_rules("203.0.113.5", 17, 0)
    assert calls[9].url.path == "/ddos-mitigation/firewall-rules/bulk"
    assert calls[9].url.params == httpx.QueryParams({"network": "203.0.113.5", "protocol": "17", "dst_port": "0"})
    assert d.list_asns(search="cloudflare")[0].asn == 13335


def test_ddos_traffic_capture() -> None:
    client, calls = make_client(
        {
            "POST /ddos-mitigation/traffic-capture": {
                "total_logs": 1,
                "logs": [{"src_ip": "192.0.2.1", "is_drop": True}],
            },
            "POST /ddos-mitigation/traffic-capture/stats": {"total_drop": 5, "buckets": [{"drop_count": 5}]},
            "GET /ddos-mitigation/traffic-capture/protected-ips": {"total": 1, "ips": [{"address": "203.0.113.5"}]},
        }
    )
    d = client.ddos_mitigation
    cap = d.capture_traffic(
        DDoSTrafficCaptureRequest(
            start_time="2026-09-30T10:00:00Z",
            end_time="2026-09-30T11:00:00Z",
            destination_ip="203.0.113.5",
            include_dst_ports=[443],
            has_payload=False,
        )
    )
    assert cap.logs[0].is_drop
    assert body(calls[0]) == {
        "start_time": "2026-09-30T10:00:00Z",
        "end_time": "2026-09-30T11:00:00Z",
        "destination_ip": "203.0.113.5",
        "include_dst_ports": [443],
        "has_payload": False,
    }
    stats = d.get_traffic_stats(DDoSTrafficStatsRequest(start_time="a", end_time="b", interval="5m"))
    assert stats.buckets[0].drop_count == 5 and body(calls[1])["interval"] == "5m"
    assert d.list_capture_ips()[0].address == "203.0.113.5"


# ── Cloud alerts ─────────────────────────────────────────────────


def test_alerts() -> None:
    alert = {
        "id": "a1",
        "project_id": 7,
        "name": "cpu",
        "target_type": "vps",
        "target_id": "12",
        "metric_type": "cpu",
        "operator": "gt",
        "threshold": 90.0,
        "status": "enabled",
        "actions": [{"id": "x", "action_type": "notify", "notificator_id": "n1"}],
    }
    client, calls = make_client(
        {
            "POST /triggers/notificators/": {"id": "n1", "name": "ops", "type": "slack", "config": {}},
            "GET /triggers/notificators/": [{"id": "n1", "type": "slack"}],
            "PUT /triggers/notificators/n1": {"id": "n1", "enabled": False},
            "POST /triggers/": alert,
            "GET /triggers/": [{**alert, "actions_count": 1}],
            "GET /triggers/a1": alert,
            "PUT /triggers/a1": {**alert, "status": "disabled"},
            "GET /triggers/a1/history": [{"id": "h1", "event_type": "triggered", "metric_value": 95.0}],
        }
    )
    a = client.alerts
    n = a.create_notificator(
        CreateNotificatorRequest(name="ops", type="slack", config={"webhook_url": "https://hooks.slack.com/x"})
    )
    assert n.id == "n1" and body(calls[0])["config"] == {"webhook_url": "https://hooks.slack.com/x"}
    assert a.list_notificators()[0].type == "slack"
    assert a.update_notificator("n1", UpdateNotificatorRequest(enabled=False)).enabled is False
    assert body(calls[2]) == {"enabled": False}

    created = a.create(
        CreateAlertRequest(
            project_id=7,
            name="cpu",
            target_type="vps",
            target_id="12",
            metric_type="cpu",
            operator="gt",
            threshold=90,
            actions=[AlertActionRequest(action_type="notify", notificator_id="n1")],
        )
    )
    assert created.actions[0].notificator_id == "n1"
    assert body(calls[3])["actions"] == [{"action_type": "notify", "order": 0, "enabled": True, "notificator_id": "n1"}]
    assert a.list(project_id=7, status="enabled")[0].actions_count == 1
    assert calls[4].url.params == httpx.QueryParams({"project_id": "7", "status": "enabled"})
    assert a.get("a1").threshold == 90.0
    assert a.update("a1", UpdateAlertRequest(status="disabled")).status == "disabled"
    assert body(calls[6]) == {"status": "disabled"}
    assert a.history("a1", limit=5)[0].metric_value == 95.0
    assert calls[7].url.params["limit"] == "5"
    a.delete("a1")
    a.delete_notificator("n1")
    assert [c.method for c in calls[8:]] == ["DELETE", "DELETE"]


# ── Transcoder ───────────────────────────────────────────────────


def test_transcoder_jobs() -> None:
    job = {
        "uuid": "j1",
        "status": "queued",
        "input": {"source": "url", "url": "https://example.com/a.mp4", "s3": None},
        "output": {"s3": {"bucket": "media", "path": "out/", "access_key": "AK"}},
        "spec": {"outputs": [{"type": "hls"}]},
        "outputs": None,
        "progress": 0,
    }
    client, calls = make_client(
        {
            "POST /transcoder/jobs": job,
            "POST /transcoder/jobs/batch": {"batch_id": "b1", "job_ids": ["j2", "j3"], "count": 2},
            "GET /transcoder/jobs": {"jobs": [job], "limit": 10, "offset": 20},
            "GET /transcoder/jobs/j1": {**job, "status": "completed", "progress": 100},
            "GET /transcoder/jobs/j1/outputs": {
                "outputs": [{"type": "hls", "bucket": "media", "key": "out/master.m3u8"}],
                "destination": {"s3": {"bucket": "media", "path": "out/"}},
            },
        }
    )
    t = client.transcoder
    out = TranscoderJobOutput(s3=TranscoderS3Config(bucket="media", path="out/", access_key="AK", secret_key="SK"))
    created = t.create_job(
        CreateTranscoderJobRequest(
            input=TranscoderJobInput(source="url", url="https://example.com/a.mp4"),
            output=out,
            outputs=[TranscoderOutputSpec(type="hls", options={"ladder": [720, 360]})],
            idempotency_key="k1",
        )
    )
    assert created.output is not None and created.output.s3.access_key == "AK" and created.output.s3.secret_key is None
    assert body(calls[0]) == {
        "input": {"source": "url", "url": "https://example.com/a.mp4"},
        "output": {"s3": {"bucket": "media", "path": "out/", "access_key": "AK", "secret_key": "SK"}},
        "outputs": [{"ladder": [720, 360], "type": "hls"}],
        "idempotency_key": "k1",
    }
    batch = t.create_batch(
        CreateTranscoderBatchRequest(
            output=out,
            outputs=[TranscoderOutputSpec(type="thumbnails")],
            input_defaults=TranscoderJobInput(source="s3", s3=TranscoderS3Config(bucket="raw")),
            inputs=[TranscoderBatchInput(path="a.mp4", out_subpath="a/"), TranscoderBatchInput(url="https://x/b.mp4")],
        )
    )
    assert batch.count == 2
    sent = body(calls[1])
    assert sent["inputs"] == [{"path": "a.mp4", "out_subpath": "a/"}, {"url": "https://x/b.mp4"}]
    assert sent["input_defaults"] == {"source": "s3", "s3": {"bucket": "raw", "path": ""}}

    listed = t.list_jobs(batch_id="b1", limit=10, offset=20)
    assert listed.offset == 20 and listed.jobs[0].uuid == "j1"
    assert calls[2].url.params == httpx.QueryParams({"limit": "10", "offset": "20", "batch_id": "b1"})
    assert t.get_job("j1").progress == 100
    outputs = t.get_job_outputs("j1")
    assert outputs.outputs[0].key == "out/master.m3u8" and outputs.destination is not None
    t.cancel_job("j1")
    assert calls[5].method == "DELETE" and calls[5].url.path == "/transcoder/jobs/j1"
