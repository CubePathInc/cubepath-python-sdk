from __future__ import annotations

from typing import TYPE_CHECKING, Any

from cubepath.models.dns import (
    CreateDNSRecordRequest,
    CreateDNSZoneRequest,
    DNSHealthCheck,
    DNSRecord,
    DNSRegion,
    DNSZone,
    SOARecord,
    UpdateDNSRecordRequest,
    UpdateSOARequest,
    UpsertDNSHealthCheckRequest,
    ZoneScanResponse,
    ZoneVerifyResponse,
)

if TYPE_CHECKING:
    from cubepath.client import CubePathClient


class DNSService:
    def __init__(self, client: CubePathClient) -> None:
        self._client = client

    # ── Zones ────────────────────────────────────────────────────

    def list_zones(self) -> list[DNSZone]:
        data: list[dict[str, Any]] = self._client.get("/dns/zones")
        return [DNSZone.from_dict(z) for z in data]

    def list_zones_by_project(self, project_id: str) -> list[DNSZone]:
        data: list[dict[str, Any]] = self._client.get("/dns/zones", params={"project_id": project_id})
        return [DNSZone.from_dict(z) for z in data]

    def get_zone(self, zone_uuid: str) -> DNSZone:
        data: dict[str, Any] = self._client.get(f"/dns/zones/{zone_uuid}")
        return DNSZone.from_dict(data)

    def create_zone(self, req: CreateDNSZoneRequest) -> DNSZone:
        data: dict[str, Any] = self._client.post("/dns/zones", json=req.to_dict())
        return DNSZone.from_dict(data)

    def delete_zone(self, zone_uuid: str) -> None:
        self._client.delete(f"/dns/zones/{zone_uuid}")

    def verify_zone(self, zone_uuid: str) -> ZoneVerifyResponse:
        data: dict[str, Any] = self._client.post(f"/dns/zones/{zone_uuid}/verify")
        return ZoneVerifyResponse.from_dict(data)

    def create_zone_from_scan(self, domain: str, project_id: int) -> ZoneScanResponse:
        """Create a zone and import the records found in public DNS: the migration path from another provider."""
        data: dict[str, Any] = self._client.post("/dns/zones/scan", params={"domain": domain, "project_id": project_id})
        return ZoneScanResponse.from_dict(data)

    def create_zone_from_file(
        self, domain: str, project_id: int, zone_file: bytes | str, filename: str = "zone.txt"
    ) -> ZoneScanResponse:
        """Create a zone and import its records from a BIND zone file."""
        data: dict[str, Any] = self._client.post(
            "/dns/zones/upload",
            params={"domain": domain, "project_id": project_id},
            files={"file": (filename, zone_file, "text/plain")},
        )
        return ZoneScanResponse.from_dict(data)

    def import_zone_file(self, zone_uuid: str, zone_file: bytes | str, filename: str = "zone.txt") -> ZoneScanResponse:
        """Import records from a BIND zone file into an existing zone."""
        data: dict[str, Any] = self._client.post(
            f"/dns/zones/{zone_uuid}/import",
            files={"file": (filename, zone_file, "text/plain")},
        )
        return ZoneScanResponse.from_dict(data)

    def move_zone_to_project(self, zone_uuid: str, project_id: int) -> None:
        self._client.post(f"/dns/zones/{zone_uuid}/move-project", json={"project_id": project_id})

    def list_regions(self) -> list[DNSRegion]:
        """GeoDNS regions a record can be restricted to."""
        data: list[dict[str, Any]] = self._client.get("/dns/regions")
        return [DNSRegion.from_dict(r) for r in data]

    def scan_zone(self, zone_uuid: str, auto_import: bool = False) -> ZoneScanResponse:
        data: dict[str, Any] = self._client.post(
            f"/dns/zones/{zone_uuid}/scan",
            params={"auto_import": str(auto_import).lower()},
        )
        return ZoneScanResponse.from_dict(data)

    # ── Records ──────────────────────────────────────────────────

    def list_records(self, zone_uuid: str) -> list[DNSRecord]:
        data: list[dict[str, Any]] = self._client.get(f"/dns/zones/{zone_uuid}/records")
        return [DNSRecord.from_dict(r) for r in data]

    def list_records_by_type(self, zone_uuid: str, record_type: str) -> list[DNSRecord]:
        data: list[dict[str, Any]] = self._client.get(
            f"/dns/zones/{zone_uuid}/records",
            params={"record_type": record_type},
        )
        return [DNSRecord.from_dict(r) for r in data]

    def create_record(self, zone_uuid: str, req: CreateDNSRecordRequest) -> DNSRecord:
        data: dict[str, Any] = self._client.post(f"/dns/zones/{zone_uuid}/records", json=req.to_dict())
        return DNSRecord.from_dict(data)

    def update_record(self, zone_uuid: str, record_uuid: str, req: UpdateDNSRecordRequest) -> DNSRecord:
        data: dict[str, Any] = self._client.put(
            f"/dns/zones/{zone_uuid}/records/{record_uuid}",
            json=req.to_dict(),
        )
        return DNSRecord.from_dict(data)

    def delete_record(self, zone_uuid: str, record_uuid: str) -> None:
        self._client.delete(f"/dns/zones/{zone_uuid}/records/{record_uuid}")

    # ── SOA ──────────────────────────────────────────────────────

    def get_soa(self, zone_uuid: str) -> SOARecord:
        data: dict[str, Any] = self._client.get(f"/dns/zones/{zone_uuid}/soa")
        return SOARecord.from_dict(data)

    def update_soa(self, zone_uuid: str, req: UpdateSOARequest) -> SOARecord:
        data: dict[str, Any] = self._client.put(f"/dns/zones/{zone_uuid}/soa", json=req.to_dict())
        return SOARecord.from_dict(data)

    # ── Health checks ────────────────────────────────────────────

    def list_health_checks(self, zone_uuid: str) -> list[DNSHealthCheck]:
        data: list[dict[str, Any]] = self._client.get(f"/dns/zones/{zone_uuid}/health-checks")
        return [DNSHealthCheck.from_dict(h) for h in data]

    def get_health_check(self, zone_uuid: str, record_uuid: str) -> DNSHealthCheck:
        data: dict[str, Any] = self._client.get(f"/dns/zones/{zone_uuid}/records/{record_uuid}/health-check")
        return DNSHealthCheck.from_dict(data)

    def set_health_check(self, zone_uuid: str, record_uuid: str, req: UpsertDNSHealthCheckRequest) -> DNSHealthCheck:
        """Create or replace the record's health check (Pro and Business tiers, billed while enabled).

        While the target fails, the record is left out of the DNS answers.
        """
        data: dict[str, Any] = self._client.put(
            f"/dns/zones/{zone_uuid}/records/{record_uuid}/health-check", json=req.to_dict()
        )
        return DNSHealthCheck.from_dict(data)

    def delete_health_check(self, zone_uuid: str, record_uuid: str) -> None:
        self._client.delete(f"/dns/zones/{zone_uuid}/records/{record_uuid}/health-check")
