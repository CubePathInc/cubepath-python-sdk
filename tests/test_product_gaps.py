from __future__ import annotations

import json
from typing import Any

import httpx

from cubepath import CubePathClient
from cubepath.models import (
    AddTargetRequest,
    CDNMetricsParams,
    CreateAvailabilityGroupRequest,
    CreateBGPPeerRequest,
    CreateDNSRecordRequest,
    UpdateBGPPeerRequest,
    UpdateCDNZoneRequest,
    UpdateDNSRecordRequest,
    UpsertDNSHealthCheckRequest,
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


def test_vps_actions() -> None:
    client, calls = make_client(
        {
            "GET /vps/plans": {
                "locations": [
                    {
                        "location_name": "eu-bcn-1",
                        "clusters": [{"cluster_name": "c1", "type": "shared", "plans": [{"plan_name": "gp.nano"}]}],
                    }
                ]
            },
            "POST /vps/5/vnc-url": {"websocket_url": "wss://x", "session_id": "s", "vnc_info": {"ticket": "t"}},
        }
    )
    vps = client.vps
    assert vps.plans()[0].clusters[0].plans[0].plan_name == "gp.nano"
    vps.configure_protection("5", True)
    vps.move_to_project("5", 9)
    vps.add_ssh_keys("5", [1, 2])
    vps.remove_ssh_key("5", 2)
    vps.attach_network("5", 73)
    vps.detach_network("5")
    console = vps.console("5")
    vps.destroy("5", release_ips=False)
    assert console.ticket == "t" and console.websocket_url == "wss://x"
    assert [(c.method, c.url.path) for c in calls[1:]] == [
        ("POST", "/vps/5/protection"),
        ("POST", "/vps/5/move-project"),
        ("POST", "/vps/5/ssh-keys"),
        ("DELETE", "/vps/5/ssh-keys/2"),
        ("POST", "/vps/5/network"),
        ("DELETE", "/vps/5/network"),
        ("POST", "/vps/5/vnc-url"),
        ("POST", "/vps/destroy/5"),
    ]
    assert body(calls[1]) == {"enabled": True}
    assert body(calls[2]) == {"project_id": 9}
    assert body(calls[3]) == [1, 2]
    assert body(calls[5]) == {"network_id": 73}
    assert body(calls[8]) == {"release_ips": False} and not calls[8].url.params


def test_vps_backups_and_isos() -> None:
    client, calls = make_client(
        {
            "GET /vps/5/backups": {
                "backups": [{"id": 3, "status": "completed", "size_gb": None}],
                "total": 1,
                "has_settings": True,
                "settings": {"enabled": True, "schedule_hour": 3, "retention_days": 7, "max_backups": 3},
            },
            "POST /vps/5/backups": {"id": 4, "status": "pending", "backup_type": "manual"},
            "GET /vps/5/isos": {"mounted_iso_id": None, "items": [{"id": "i1", "filename": "x.iso"}]},
        }
    )
    backups = client.vps.backups()
    assert backups.list("5")[0].status == "completed"
    full = backups.list_with_settings("5")
    assert full.settings is not None and full.settings.max_backups == 3
    assert backups.create("5").id == 4
    backups.restore("5", "3")
    assert calls[3].url.path == "/vps/5/backups/3/restore" and body(calls[3]) == {"confirm": True}
    isos = client.vps.isos().list("5")
    assert isos.mounted_iso_id == "" and isos.items[0].filename == "x.iso"


def test_availability_groups() -> None:
    group = {"uuid": "g1", "project_id": 7, "name": "web", "strategy": "spread", "vps_list": [{"id": 5, "name": "a"}]}
    client, calls = make_client(
        {
            "GET /vps/availability-groups/project/7": {"groups": [group]},
            "GET /vps/availability-groups/g1": group,
            "POST /vps/availability-groups/": {"detail": "ok", **group},
        }
    )
    ag = client.vps.availability_groups()
    assert ag.list(7, "eu-bcn-1")[0].vps_list[0].id == 5
    assert calls[0].url.params["location_name"] == "eu-bcn-1"
    assert ag.get("g1").strategy == "spread"
    created = ag.create(CreateAvailabilityGroupRequest(project_id=7, name="web", location_name="eu-bcn-1"))
    assert created.uuid == "g1" and body(calls[2]) == {"project_id": 7, "name": "web", "location_name": "eu-bcn-1"}
    ag.add_vps("g1", 5)
    ag.remove_vps("g1", 5)
    ag.move_to_project("g1", 8)
    ag.delete("g1")
    assert [(c.method, c.url.path) for c in calls[3:]] == [
        ("POST", "/vps/availability-groups/g1/vps/5"),
        ("DELETE", "/vps/availability-groups/g1/vps/5"),
        ("POST", "/vps/availability-groups/g1/move-project"),
        ("DELETE", "/vps/availability-groups/g1"),
    ]


def test_baremetal_actions() -> None:
    client, calls = make_client(
        {
            "GET /baremetal/models": {
                "locations": [{"location_name": "eu-bcn-1", "models": [{"model_name": "m1", "stock_available": 2}]}]
            },
            "GET /baremetal/9/kvm": {"url": "https://kvm", "username": "admin", "password": "pw"},
            "GET /baremetal/os/9": [{"id": 1, "os_name": "debian-12", "disk_layouts": [{"id": 2, "name": "raid1"}]}],
        }
    )
    bm = client.baremetal
    assert bm.list_models()[0].models[0].stock_available == 2
    assert bm.kvm("9").password == "pw"
    assert bm.list_os("9")[0].disk_layouts[0].name == "raid1"
    bm.configure_protection("9", False)
    bm.move_to_project("9", 4)
    bm.add_ssh_keys("9", [1])
    bm.remove_ssh_key("9", 1)
    bm.attach_network("9", 73)
    bm.detach_network("9")
    assert [(c.method, c.url.path) for c in calls[3:]] == [
        ("POST", "/baremetal/9/protection"),
        ("POST", "/baremetal/9/move-project"),
        ("POST", "/baremetal/9/ssh-keys"),
        ("DELETE", "/baremetal/9/ssh-keys/1"),
        ("POST", "/baremetal/9/network"),
        ("DELETE", "/baremetal/9/network"),
    ]
    assert body(calls[3]) == {"enabled": False} and body(calls[5]) == [1]


def test_network_bgp_peers_and_create_ids() -> None:
    client, calls = make_client(
        {
            "POST /networks/create_network": {"detail": "ok", "network_id": 73, "name": "n", "location": "eu-bcn-1"},
            "GET /networks/73/bgp-peers": [{"id": "p1", "remote_asn": 65010, "received_prefixes": ["10.9.0.0/16"]}],
            "POST /networks/73/bgp-peers": {"detail": "ok", "peer_id": "p2", "peer_type": "vps", "remote_asn": 65010},
        }
    )
    from cubepath.models import CreateNetworkRequest

    net = client.networks.create(
        CreateNetworkRequest(name="n", location_name="eu-bcn-1", ip_range="10.0.0.0", prefix=16, project_id="7")
    )
    assert net.id == 73 and net.location_name == "eu-bcn-1"
    assert client.networks.list_bgp_peers("73")[0].received_prefixes == ["10.9.0.0/16"]
    peer = client.networks.create_bgp_peer(
        "73", CreateBGPPeerRequest(peer_type="vps", peer_target="5", remote_asn=65010)
    )
    assert peer.id == "p2"
    assert body(calls[2]) == {"peer_type": "vps", "peer_target": "5", "remote_asn": 65010, "max_prefix": 100}
    client.networks.update_bgp_peer("73", "p2", UpdateBGPPeerRequest(enabled=False))
    client.networks.delete_bgp_peer("73", "p2")
    client.networks.move_to_project("73", 8)
    assert [(c.method, c.url.path) for c in calls[3:]] == [
        ("PATCH", "/networks/73/bgp-peers/p2"),
        ("DELETE", "/networks/73/bgp-peers/p2"),
        ("POST", "/networks/73/move-project"),
    ]
    assert body(calls[3]) == {"enabled": False}


def test_cdn_purge_token_auth_and_metrics() -> None:
    client, calls = make_client(
        {
            "POST /cdn/zones/z1/purge-cache": {"detail": "queued", "purge_uuid": "pu1", "status": "pending"},
            "GET /cdn/zones/z1/purge-cache": [
                {
                    "purge_uuid": "pu1",
                    "scope": "paths",
                    "paths": ["/a"],
                    "status": "completed",
                    "nodes": {"expected": 4, "completed": 4, "failed": 0},
                    "pops": [{"pop": "bcn", "expected": 2, "completed": 2, "failed": 0}],
                }
            ],
            "POST /cdn/zones/z1/token-auth/rotate-secret": {"detail": "ok", "token_auth_secret": "s3cret"},
            "POST /cdn/zones/z1/token-auth/sign-url": {"signed_url": "https://x/a?t=1", "token": "t", "expires": 99},
            "PATCH /cdn/zones/z1": {"uuid": "z1", "token_auth_enabled": True, "token_auth_secret": "first"},
        }
    )
    cdn = client.cdn
    assert cdn.purge_cache("z1", paths=["/a"]).purge_uuid == "pu1"
    assert body(calls[0]) == {"everything": False, "paths": ["/a"]}
    purge = cdn.list_purges("z1")[0]
    assert purge.nodes_completed == 4 and purge.pops[0].pop == "bcn"
    assert cdn.rotate_token_secret("z1") == "s3cret"
    signed = cdn.sign_url("z1", "/a", expires_in=60)
    assert signed.expires == 99 and body(calls[3]) == {"path": "/a", "expires_in": 60}
    zone = cdn.update_zone("z1", UpdateCDNZoneRequest(token_auth_enabled=True, cors_enabled=False))
    assert zone.token_auth_secret == "first"
    assert body(calls[4]) == {"token_auth_enabled": True, "cors_enabled": False}

    cdn.get_metrics_top_urls("z1", CDNMetricsParams(minutes=1440, limit=5, country="ES"))
    cdn.get_metrics_file_extensions("z1")
    assert calls[5].url.path == "/cdn/zones/z1/metrics/top-urls"
    assert calls[5].url.params == httpx.QueryParams({"minutes": "1440", "limit": "5", "country": "ES"})
    assert calls[6].url.path == "/cdn/zones/z1/metrics/file-extensions"


def test_dns_health_checks_regions_and_import() -> None:
    hc = {"uuid": "h1", "record_uuid": "r1", "check_type": "https", "last_status": "healthy"}
    client, calls = make_client(
        {
            "GET /dns/regions": [{"code": "eu-west", "name": "Amsterdam"}],
            "GET /dns/zones/z1/health-checks": [hc],
            "GET /dns/zones/z1/records/r1/health-check": hc,
            "PUT /dns/zones/z1/records/r1/health-check": hc,
            "POST /dns/zones/upload": {"imported": 2, "skipped": 0, "errors": [], "records": []},
            "POST /dns/zones/z1/import": {"imported": 1, "records": [{"uuid": "r2", "region": "eu-west"}]},
            "POST /dns/zones/scan": {"imported": 3},
        }
    )
    dns = client.dns
    assert dns.list_regions()[0].code == "eu-west"
    assert dns.list_health_checks("z1")[0].last_status == "healthy"
    assert dns.get_health_check("z1", "r1").check_type == "https"
    dns.set_health_check("z1", "r1", UpsertDNSHealthCheckRequest(name="api", check_type="https", path="/health"))
    assert calls[3].method == "PUT" and body(calls[3]) == {
        "name": "api",
        "check_type": "https",
        "path": "/health",
        "expected_status": 200,
        "interval_secs": 60,
        "timeout_secs": 5,
        "healthy_threshold": 2,
        "unhealthy_threshold": 3,
        "enabled": True,
    }
    dns.delete_health_check("z1", "r1")
    assert calls[4].method == "DELETE"

    zone_file = b"www 300 IN A 203.0.113.5\n"
    assert dns.create_zone_from_file("example.com", 7, zone_file).imported == 2
    upload = calls[5]
    assert upload.url.params == httpx.QueryParams({"domain": "example.com", "project_id": "7"})
    assert upload.headers["content-type"].startswith("multipart/form-data")
    assert zone_file in upload.content
    assert dns.import_zone_file("z1", zone_file.decode()).records[0].region == "eu-west"
    assert dns.create_zone_from_scan("example.com", 7).imported == 3
    dns.move_zone_to_project("z1", 8)
    assert body(calls[8]) == {"project_id": 8}

    rec = CreateDNSRecordRequest(name="www", record_type="A", content="203.0.113.5", ttl=300, region="eu-west")
    assert rec.to_dict()["region"] == "eu-west"
    assert UpdateDNSRecordRequest(comment="", region="global").to_dict() == {"comment": "", "region": "global"}


def test_load_balancer_kubernetes_ssh_and_projects() -> None:
    client, calls = make_client(
        {
            "POST /loadbalancer/lb1/listeners/l1/targets/batch": {
                "detail": "ok",
                "targets": [{"uuid": "t1", "target_type": "vps", "target_uuid": "5"}],
            },
            "GET /kubernetes/c1/metrics": {"start": 1, "end": 2, "step": 60, "metrics": {"nodes_ready": [[1, 3]]}},
            "GET /kubernetes/c1/nodes/n1/metrics": {"step": 60, "metrics": {}},
            "GET /sshkey/user/sshkeys": {"sshkeys": [{"id": 1, "name": "laptop"}]},
            "PUT /sshkey/1": {"detail": "ok", "sshkey": {"id": 1, "name": "desk"}},
            "POST /sshkey/create": {"detail": "ok", "ssh_key_id": 2, "name": "new"},
            "POST /projects/": {"detail": "ok", "project_id": 11, "name": "p"},
        }
    )
    targets = client.load_balancer.add_targets(
        "lb1", "l1", [AddTargetRequest(target_type="vps", target_uuid="5", weight=10, port=8080)]
    )
    assert targets[0].uuid == "t1"
    assert body(calls[0]) == {"targets": [{"target_type": "vps", "target_uuid": "5", "weight": 10, "port": 8080}]}
    client.load_balancer.configure_protection("lb1", True)
    client.load_balancer.move_to_project("lb1", 3)
    assert [c.url.path for c in calls[1:3]] == ["/loadbalancer/lb1/protection", "/loadbalancer/lb1/move-project"]

    assert client.kubernetes.get_metrics("c1", "24h").metrics["nodes_ready"] == [[1, 3]]
    assert calls[3].url.params["time_range"] == "24h"
    assert client.kubernetes.get_node_metrics("c1", "n1").step == 60
    client.kubernetes.configure_protection("c1", True)
    assert calls[5].url.path == "/kubernetes/c1/protection" and body(calls[5]) == {"enabled": True}

    assert client.ssh_keys.list()[0].name == "laptop"
    assert client.ssh_keys.update("1", "desk").name == "desk"
    assert body(calls[7]) == {"name": "desk"}
    from cubepath.models import CreateProjectRequest, CreateSSHKeyRequest

    assert client.ssh_keys.create(CreateSSHKeyRequest(name="new", ssh_key="ssh-ed25519 AAAA")).id == 2
    assert client.projects.create(CreateProjectRequest(name="p")).id == 11
    client.projects.update("11", "renamed")
    assert calls[10].method == "PUT" and body(calls[10]) == {"name": "renamed"}
