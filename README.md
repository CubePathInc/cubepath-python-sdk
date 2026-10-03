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
| Object Storage | `client.object_storage` | S3 compatible buckets, access keys, replication, usage |
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

# Charts of one bucket (GraphQL): stored size and objects, traffic and responses per step
# over H1, H3, H6, H12, H24 (default), D3, D7 or D30
metrics = client.object_storage.get_bucket_metrics(bucket.uuid, "D7")

# Buckets are private: serve one publicly through a CDN zone
client.cdn.create_origin(zone.uuid, CreateCDNOriginRequest(
    name="my-bucket", weight=100, priority=1, object_storage_bucket_uuid=bucket.uuid,
))

client.object_storage.delete_key(key.uuid)
client.object_storage.delete_bucket(bucket.uuid, force=True)  # force purges the content first
```

#### Object Lock

Object Lock (WORM) keeps object versions from being deleted or overwritten until their
retention date. It can only be enabled when the bucket is created, never later; the bucket
always keeps versioning enabled and is created with deletion protection on.

- `governance`: keys created with `bypass_governance` can still delete a version early (sending
  `x-amz-bypass-governance-retention: true`).
- `compliance`: nobody can delete a version or shorten its retention before the date, CubePath
  included. Only organizations that support enabled for it can use it.

```python
from cubepath.models import ObjectStorageLockRetention, SetObjectStorageObjectLockRequest

vault = client.object_storage.create_bucket(CreateObjectStorageBucketRequest(
    name="veeam-repo",
    tier="infrequent_access",
    object_lock=True,  # implies versioning
    object_lock_default=ObjectStorageLockRetention(mode="governance", days=30),  # or years=
    accept_object_lock_terms=True,
))
print(vault.object_lock.enabled)

# Change the default retention (a compliance rule can only be kept or lengthened).
# accept_object_lock_terms is needed when the rule turns compliance on or gets longer.
client.object_storage.set_bucket_object_lock(vault.uuid, SetObjectStorageObjectLockRequest(
    default_retention=ObjectStorageLockRetention(mode="governance", years=1),
    accept_object_lock_terms=True,
))
client.object_storage.set_bucket_object_lock(vault.uuid, SetObjectStorageObjectLockRequest())  # remove it

# A key that may delete governance versions early (read_write only)
client.object_storage.create_key(CreateObjectStorageAccessKeyRequest(
    name="veeam", tier="infrequent_access", permission="read_write", bypass_governance=True,
))

# Delete: disable protection first. bypass_governance (with force) also purges governance
# versions. Versions under compliance or a legal hold are kept: the bucket stays with
# locked_content_kept set and keeps being billed until their retention ends.
client.object_storage.delete_bucket(vault.uuid, force=True, bypass_governance=True)
```

#### Replication

Replication copies every new object version of a source bucket to one destination, object by
object and asynchronously: another CubePath bucket of the same tier, or an external S3 compatible
bucket (AWS S3, Wasabi or another provider with versioning) over HTTPS on port 443 only.

- Versioning must be enabled on the source (and on a CubePath destination) and cannot be suspended
  while the bucket replicates. Buckets with Object Lock cannot be sources; a destination with
  Object Lock is fine.
- A CubePath destination lives on the same storage cluster as the source: it protects against
  mistakes, not against the loss of the site, so it is not disaster recovery. For an off site copy
  use an external destination.
- Replication to an external destination is billed as egress of the source bucket (the initial copy
  of existing objects included) and shares the organization's free egress. A CubePath destination
  has no egress cost; the replicas are billed as storage of the destination bucket.
- One destination per source bucket. A bucket cannot be a source and a destination at once.
- To replicate into a bucket of another organization, its owner creates a one use grant and hands
  you the token.

```python
from cubepath.models import (
    CreateObjectStorageReplicationGrantRequest,
    CreateObjectStorageReplicationRequest,
    ObjectStorageReplicationDestinationRequest,
    UpdateObjectStorageReplicationRequest,
)

# To a CubePath bucket (grant_token only for a bucket of another organization)
repl = client.object_storage.create_replication(CreateObjectStorageReplicationRequest(
    source_bucket_uuid=bucket.uuid,
    destination=ObjectStorageReplicationDestinationRequest.cubepath(dest_bucket_uuid),
    prefix="img/",           # or tags=[ObjectStorageReplicationTag(key="backup", value="yes")]
    existing_objects=True,   # also copy what the bucket already holds
))

# To an external provider: the secret is never returned
client.object_storage.create_replication(CreateObjectStorageReplicationRequest(
    source_bucket_uuid=other_bucket.uuid,
    destination=ObjectStorageReplicationDestinationRequest.external(
        provider="aws", endpoint="s3.eu-west-1.amazonaws.com", region="eu-west-1",
        bucket="acme-backup", access_key_id=os.environ["AWS_KEY"], secret_access_key=os.environ["AWS_SECRET"],
    ),
))

detail = client.object_storage.get_replication(repl.uuid)  # status, health, backfill, metrics
client.object_storage.list_replications(direction="outgoing")  # or "incoming", "all"
client.object_storage.update_replication(repl.uuid, UpdateObjectStorageReplicationRequest(enabled=False))  # pause
client.object_storage.update_replication(repl.uuid, UpdateObjectStorageReplicationRequest(clear_prefix=True))
client.object_storage.resync_replication(repl.uuid, older_than_days=7)  # send existing objects again
client.object_storage.delete_replication(repl.uuid)  # replicated data stays in the destination

# Owner of the destination bucket, in the other organization
grant = client.object_storage.create_replication_grant(
    dest_bucket_uuid, CreateObjectStorageReplicationGrantRequest(note="for Acme", expires_in_days=7)
)
print(grant.token)  # shown only once
client.object_storage.list_replication_grants(dest_bucket_uuid)
client.object_storage.delete_replication_grant(grant.uuid)  # revoke while unused
client.object_storage.revoke_replication(incoming_replication_uuid)  # stop an incoming replication
```

#### Event Notifications

Send bucket events (`object.created`, `object.removed`, `object.tagging`) to a signed webhook
or to a Cloud Alerts channel. A destination belongs to the organization; a rule on a bucket picks
the events, an optional key prefix and suffix, and the destination. The signing secret is only
returned by `create_event_destination` and `rotate_event_destination_secret`: store it then.
After a rotation the previous secret keeps signing for 24 hours.

```python
from cubepath.models import CreateObjectStorageEventDestinationRequest, CreateObjectStorageEventRuleRequest

created = client.object_storage.create_event_destination(
    CreateObjectStorageEventDestinationRequest(
        name="uploads-hook", type="webhook", url="https://example.com/hooks/storage"
    )  # or type="notificator", notificator_id=channel_id
)
secret = created.signing_secret  # whsec_..., shown only now

rule = client.object_storage.create_event_rule(
    bucket.uuid,
    CreateObjectStorageEventRuleRequest(
        name="new-uploads", destination_uuid=created.destination.uuid, events=["object.created"], prefix="incoming/"
    ),
)  # rule.status is "pending" until applied, then "active"

client.object_storage.test_event_destination(created.destination.uuid)  # sends a cubepath.ping
page = client.object_storage.list_event_deliveries(created.destination.uuid, status="failed", limit=20)
# Older page: before=page.next_before (unix milliseconds) while it is not None.
```

Verify every webhook delivery before trusting it, against the raw body. `CubePath-Signature`
holds one or more `v1=<hex>` values (`v1=<new>, v1=<previous>` for 24 hours after a rotation), each the HMAC-SHA256 of `CubePath-Timestamp + "." + body`;
`verify_storage_event_signature` compares them in constant time and rejects timestamps more than
5 minutes away:

```python
from cubepath import StorageEventSignatureError, verify_storage_event_signature

@app.post("/hooks/storage")
def storage_hook():
    try:
        verify_storage_event_signature(
            secret,
            request.headers.get("CubePath-Timestamp", ""),
            request.get_data(),
            request.headers.get("CubePath-Signature", ""),
        )
    except StorageEventSignatureError:
        return "", 401
    # Deliveries are at least once: deduplicate by the CubePath-Event-Id header.
    return "", 204
```

#### Presigned URLs

This SDK talks to the CubePath API, not to S3. To share one object for a while, sign a
presigned GET URL with the official S3 SDK and one of your access keys: endpoint
`https://eu.cubestorage.io`, region `eu`, path style, SigV4. A URL lasts at most 24 hours
(86400 seconds), the file is always downloaded as an attachment (do not set
`ResponseContentDisposition` or any other `response-*` override: they are refused) and every
download counts as egress of the bucket. Deleting the access key that signed a URL cuts it
before it expires. From a terminal, `cubecli s3 presign <bucket>/<key> --expires 6h` does the
same.

```python
import boto3
from botocore.config import Config

s3 = boto3.client(
    "s3",
    endpoint_url="https://eu.cubestorage.io",
    region_name="eu",
    aws_access_key_id=key.access_key_id,
    aws_secret_access_key=key.secret_access_key,
    config=Config(signature_version="s3v4", s3={"addressing_style": "path"}),
)
url = s3.generate_presigned_url(
    "get_object", Params={"Bucket": "my-backups", "Key": "reports/2026-09.pdf"}, ExpiresIn=86400
)
```

Lifecycle rules delete objects in the background, permanently. `put_bucket_lifecycle` replaces every
rule and is applied asynchronously (seconds, up to about 12 minutes after a previous change of the same
bucket); objects go within 48 hours of their due date. In a versioned bucket an expiration only adds
a delete marker: add a `noncurrent_version_expiration` rule to free space.

```python
change = client.object_storage.put_bucket_lifecycle(bucket.uuid, [
    {"id": "logs-30d", "enabled": True, "filter": {"prefix": "logs/"}, "expiration": {"days": 30}},
    {"id": "old-versions", "enabled": True, "noncurrent_version_expiration": {"noncurrent_days": 30}},
])
lifecycle = client.object_storage.get_bucket_lifecycle(bucket.uuid)  # lifecycle.applied once done
client.object_storage.delete_bucket_lifecycle(bucket.uuid)
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
