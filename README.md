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
| Availability Groups | `client.vps.availability_groups()` | Spread groups of VPS |
| Baremetal | `client.baremetal` | Bare metal servers |
| Networks | `client.networks` | Private networks, routes, BGP peers |
| Floating IPs | `client.floating_ips` | Floating IP addresses |
| Firewall | `client.firewall` | Firewall groups & rules |
| DNS | `client.dns` | DNS zones & records |
| Load Balancer | `client.load_balancer` | Load balancers, listeners, targets |
| CDN | `client.cdn` | CDN zones, origins, rules, WAF, cache purge, signed URLs, metrics |
| Object Storage | `client.object_storage` | S3 compatible buckets, access keys, usage |
| Kubernetes | `client.kubernetes` | K8s clusters, node pools, addons, metrics |
| Managed Databases | `client.managed_databases` | Managed MySQL, Valkey and PostgreSQL |
| Pricing | `client.pricing` | Pricing information |
| DDoS | `client.ddos` | DDoS attack reports |
| DDoS Mitigation | `client.ddos_mitigation` | Premium protection profiles, filters, firewall rules, traffic capture |
| Cloud Alerts | `client.alerts` | Metric alerts and notification channels |
| Transcoder | `client.transcoder` | Video transcoding jobs |

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

### Object Storage

Buckets and keys are created asynchronously: poll until `status` is `active`. Use any S3
client (boto3, rclone, aws cli) with the key against the tier `endpoint`.

```python
from cubepath.models import (
    CreateCDNOriginRequest,
    CreateObjectStorageAccessKeyRequest,
    CreateObjectStorageBucketRequest,
    UpdateObjectStorageBucketRequest,
)

tiers = client.object_storage.list_tiers()

bucket = client.object_storage.create_bucket(CreateObjectStorageBucketRequest(
    name="my-backups",
    tier="infrequent_access",
    project_id=12,
))
detail = client.object_storage.get_bucket(bucket.uuid)  # connection info, month usage, CDN origin
client.object_storage.update_bucket(bucket.uuid, UpdateObjectStorageBucketRequest(versioning="enabled"))

# The secret is only returned here
key = client.object_storage.create_key(CreateObjectStorageAccessKeyRequest(
    name="backups",
    tier="infrequent_access",
    permission="read_write",
    bucket_uuids=[bucket.uuid],  # omit for every bucket of the project
))
print(key.access_key_id, key.secret_access_key, key.endpoint, key.region)

usage = client.object_storage.get_usage(period="2026-09")

# Buckets are private: serve one publicly through a CDN zone
client.cdn.create_origin(zone.uuid, CreateCDNOriginRequest(
    name="my-bucket", weight=100, priority=1, object_storage_bucket_uuid=bucket.uuid,
))

client.object_storage.delete_key(key.uuid)
client.object_storage.delete_bucket(bucket.uuid, force=True)  # force purges the content first
```

### Managed Databases

Databases are created asynchronously: poll `get()` until `status` is `active`. The plan
decides the location and the per-node size; the price is per node.

```python
import time

from cubepath.models import CreateManagedDatabaseRequest, CreateManagedDatabaseUserRequest

locations = client.managed_databases.list_plans(engine="postgresql")
plan = locations[0].plans[0]

db = client.managed_databases.create(CreateManagedDatabaseRequest(
    project_id=12,
    name="app-db",
    engine="postgresql",
    version="17.5.0",
    plan_uuid=plan.uuid,
    replicas=2,
))
while client.managed_databases.get(db.uuid).status != "active":
    time.sleep(30)

creds = client.managed_databases.get_credentials(db.uuid)
print(creds.uri)

client.managed_databases.create_database(db.uuid, "app")
user = client.managed_databases.create_user(db.uuid, CreateManagedDatabaseUserRequest(username="app"))
print(user.password)  # only returned here

client.managed_databases.scale(db.uuid, replicas=3)
client.managed_databases.update_config(db.uuid, {"max_connections": 200})
client.managed_databases.delete(db.uuid)
```

### DDoS Mitigation

Profiles, traffic capture and stats need an IP with Premium protection; firewall rules and
prefix lists work on any IP of the organization.

```python
from cubepath.models import CreateDDoSFirewallRuleRequest

ips = client.ddos_mitigation.list_ips()

profile = client.ddos_mitigation.get_profile("203.0.113.5")
req = profile.to_request()  # an update replaces the whole profile
req.country_mode = 2        # whitelist
client.ddos_mitigation.update_profile("203.0.113.5", req)
client.ddos_mitigation.set_profile_countries("203.0.113.5", ["ES", "FR"])

client.ddos_mitigation.create_firewall_rule(CreateDDoSFirewallRuleRequest(
    network="203.0.113.5", protocol=17, dst_port=0, action=0,  # drop all UDP
))
rules = client.ddos_mitigation.list_firewall_rules("203.0.113.5")
```

### Cloud Alerts

```python
from cubepath.models import AlertActionRequest, CreateAlertRequest, CreateNotificatorRequest

channel = client.alerts.create_notificator(CreateNotificatorRequest(
    name="ops", type="slack", config={"webhook_url": "https://hooks.slack.com/services/..."},
))
alert = client.alerts.create(CreateAlertRequest(
    project_id=12,
    name="High CPU",
    target_type="vps",
    target_id="1234",
    metric_type="cpu",
    operator="gt",
    threshold=90,
    actions=[AlertActionRequest(action_type="notify", notificator_id=channel.id)],
))
history = client.alerts.history(alert.id)
```

### Video Transcoder

Output always goes to your own S3 compatible bucket (for example a CubePath Object Storage
bucket and access key).

```python
from cubepath.models import (
    CreateTranscoderJobRequest,
    TranscoderJobInput,
    TranscoderJobOutput,
    TranscoderOutputSpec,
    TranscoderS3Config,
)

job = client.transcoder.create_job(CreateTranscoderJobRequest(
    input=TranscoderJobInput(source="url", url="https://example.com/video.mp4"),
    output=TranscoderJobOutput(s3=TranscoderS3Config(
        bucket="media", path="videos/out/", endpoint="https://eu.cubestorage.io", region="eu",
        access_key="...", secret_key="...",
    )),
    outputs=[TranscoderOutputSpec(type="file", options={"codec": "h264", "height": 720, "container": "mp4"})],
))
while client.transcoder.get_job(job.uuid).status not in ("completed", "failed", "canceled"):
    time.sleep(10)
print(client.transcoder.get_job_outputs(job.uuid).outputs)
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
