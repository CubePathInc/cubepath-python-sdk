# CubePath Python SDK

Official Python SDK for the [CubePath Cloud API](https://api.cubepath.com).

## Installation

```bash
pip install cubepath
```

## Quick Start

```python
import cubepath

client = cubepath.CubePathClient(api_token="your-api-token")

# List projects
projects = client.projects.list()
for p in projects:
    print(p.project.name)

# Create a VPS
from cubepath.models import CreateVPSRequest

req = CreateVPSRequest(
    name="my-vps",
    plan_name="gp.nano",
    template_name="debian-12",
    location_name="us-mia-1",
    ssh_key_ids=[12],
)
task = client.vps.create(project_id="proj-123", req=req)
print(f"Task: {task.task_id}")
```

## Services

| Service | Access | Description |
|---------|--------|-------------|
| Projects | `client.projects` | Manage projects |
| SSH Keys | `client.ssh_keys` | Manage SSH keys |
| VPS | `client.vps` | Virtual private servers |
| VPS Backups | `client.vps.backups()` | VPS backup management |
| VPS ISOs | `client.vps.isos()` | ISO mount/unmount |
| Baremetal | `client.baremetal` | Bare metal servers |
| Networks | `client.networks` | Private networks |
| Floating IPs | `client.floating_ips` | Floating IP addresses |
| Firewall | `client.firewall` | Firewall groups & rules |
| DNS | `client.dns` | DNS zones & records |
| Load Balancer | `client.load_balancer` | Load balancers, listeners, targets |
| CDN | `client.cdn` | CDN zones, origins, rules, WAF |
| Kubernetes | `client.kubernetes` | K8s clusters, node pools, addons |
| Pricing | `client.pricing` | Pricing information |
| DDoS | `client.ddos` | DDoS attack reports |

## Configuration

```python
client = cubepath.CubePathClient(
    api_token="your-api-token",
    base_url="https://api.cubepath.com",   # default
    timeout=30.0,                           # seconds
    max_retries=3,                          # retry on 429/5xx
    retry_wait_min=1.0,                     # min backoff seconds
    retry_wait_max=30.0,                    # max backoff seconds
    rate_limit_interval=0.1,                # 10 req/s
)
```

## Context Manager

```python
with cubepath.CubePathClient(api_token="tok") as client:
    zones = client.dns.list_zones()
```

## Error Handling

```python
from cubepath import APIError, is_not_found

try:
    project = client.projects.get("nonexistent")
except APIError as e:
    if e.is_not_found():
        print("Project not found")
    elif e.is_rate_limited():
        print("Rate limited, try again later")
    else:
        print(f"API error: {e}")
```

## Requirements

- Python >= 3.10
- httpx >= 0.27

## Examples

### Deploy a Baremetal Server

```python
from cubepath.models import CreateBaremetalRequest

req = CreateBaremetalRequest(
    model_name="c1.metal.plus",
    location_name="us-mia-1",
    hostname="db-server",
    password="SecurePass123!",
    os_name="debian-12",
    ssh_key_ids=[12],
)
task = client.baremetal.deploy(project_id="proj-123", req=req)
```

### Create a Load Balancer

```python
from cubepath.models import CreateLoadBalancerRequest, CreateListenerRequest

lb = client.load_balancer.create(CreateLoadBalancerRequest(
    name="web-lb",
    plan_name="lb.small",
    location_name="us-mia-1",
))

client.load_balancer.create_listener(lb.uuid, CreateListenerRequest(
    name="http",
    protocol="http",
    source_port=80,
    target_port=8080,
    algorithm="round_robin",
))
```

### Create a CDN Zone

```python
from cubepath.models import CreateCDNZoneRequest, CreateCDNOriginRequest

zone = client.cdn.create_zone(CreateCDNZoneRequest(
    name="my-site",
    plan_name="cdn.starter",
    custom_domain="cdn.example.com",
))

client.cdn.create_origin(zone.uuid, CreateCDNOriginRequest(
    name="primary-origin",
    address="origin.example.com",
    port=443,
    protocol="https",
    weight=100,
    priority=1,
    health_check_path="/health",
))
```

### DNS Management

```python
from cubepath.models import CreateDNSZoneRequest, CreateDNSRecordRequest

zone = client.dns.create_zone(CreateDNSZoneRequest(domain="example.com"))

client.dns.create_record(zone.uuid, CreateDNSRecordRequest(
    name="@",
    record_type="A",
    content="203.0.113.10",
    ttl=3600,
))
```
