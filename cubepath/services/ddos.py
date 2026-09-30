from __future__ import annotations

from typing import TYPE_CHECKING, Any

from cubepath.models.ddos import (
    CreateDDoSFirewallRuleRequest,
    DDoSASN,
    DDoSAttack,
    DDoSCaptureIP,
    DDoSCountry,
    DDoSFirewallRule,
    DDoSIPList,
    DDoSPrefixList,
    DDoSProtectionProfile,
    DDoSTrafficCapture,
    DDoSTrafficCaptureRequest,
    DDoSTrafficStats,
    DDoSTrafficStatsRequest,
    UpdateDDoSProtectionProfileRequest,
)

if TYPE_CHECKING:
    from cubepath.client import CubePathClient


class DDoSService:
    """DDoS attacks detected on your IPs."""

    def __init__(self, client: CubePathClient) -> None:
        self._client = client

    def list_attacks(self) -> list[DDoSAttack]:
        data: Any = self._client.get("/ddos-attacks/attacks")
        # With no recent attack the API answers {"detail": "No recent DDoS attacks were found..."}
        if not isinstance(data, list):
            return []
        return [DDoSAttack.from_dict(a) for a in data]

    def get_attack_details(self, attack_id: int | str) -> Any:
        """Detailed samples of one of the latest 100 attacks, as returned by the detection system.

        An empty list means no details were recorded.
        """
        return self._client.get(f"/ddos-attacks/attacks/{attack_id}/details")

    def get_attack_traffic_graph(self, attack_id: int | str) -> Any:
        """Traffic time series of one of the latest 100 attacks, as returned by the detection system."""
        return self._client.get(f"/ddos-attacks/attacks/{attack_id}/traffic-graph")


class DDoSMitigationService:
    """Premium DDoS protection: per-IP profiles, geo/ASN/prefix filtering, firewall rules and traffic capture.

    ``network`` is a single IP, or a CIDR where the endpoint accepts subnets.
    """

    def __init__(self, client: CubePathClient) -> None:
        self._client = client

    # ── Protected IPs ────────────────────────────────────────────

    def list_ips(
        self, *, ip_type: str | None = None, location: str | None = None, has_profile: bool | None = None
    ) -> DDoSIPList:
        """IPs and subnets of the organization with Premium protection."""
        params: dict[str, Any] = {}
        if ip_type:
            params["ip_type"] = ip_type
        if location:
            params["location"] = location
        if has_profile is not None:
            params["has_profile"] = str(has_profile).lower()
        data: dict[str, Any] = self._client.get("/ddos-mitigation/ips", params=params or None)
        return DDoSIPList.from_dict(data)

    # ── Profiles ─────────────────────────────────────────────────

    def get_profile(self, network: str) -> DDoSProtectionProfile:
        """Protection profile of a Premium IP or subnet (defaults when none was saved)."""
        data: dict[str, Any] = self._client.get(f"/ddos-mitigation/profiles/{network}")
        return DDoSProtectionProfile.from_dict(data)

    def update_profile(self, network: str, req: UpdateDDoSProtectionProfileRequest) -> None:
        """Replace the whole profile of a Premium IP, or of every IP of an IPv4 subnet."""
        self._client.put(f"/ddos-mitigation/profiles/{network}", json=req.to_dict())

    def delete_profile(self, network: str) -> None:
        """Remove the profile, back to the default protection."""
        self._client.delete(f"/ddos-mitigation/profiles/{network}")

    def get_profile_countries(self, network: str) -> list[DDoSCountry]:
        data: dict[str, Any] = self._client.get(f"/ddos-mitigation/profiles/{network}/countries")
        return [DDoSCountry.from_dict(c) for c in data.get("countries", [])]

    def set_profile_countries(self, network: str, iso_codes: list[str]) -> None:
        """Replace the countries the profile's country_mode applies to (ISO 3166 alpha-2 codes)."""
        self._client.put(f"/ddos-mitigation/profiles/{network}/countries", json={"iso_codes": iso_codes})

    def get_profile_asns(self, network: str) -> list[DDoSASN]:
        data: dict[str, Any] = self._client.get(f"/ddos-mitigation/profiles/{network}/asns")
        return [DDoSASN.from_dict(a) for a in data.get("asns", [])]

    def set_profile_asns(self, network: str, asns: list[int]) -> None:
        """Replace the ASNs the profile's asn_mode applies to."""
        self._client.put(f"/ddos-mitigation/profiles/{network}/asns", json={"asns": asns})

    def get_profile_prefix_lists(self, network: str) -> list[DDoSPrefixList]:
        data: dict[str, Any] = self._client.get(f"/ddos-mitigation/profiles/{network}/prefix-lists")
        return [DDoSPrefixList.from_dict(p) for p in data.get("prefix_lists", [])]

    def set_profile_prefix_lists(self, network: str, uuids: list[str]) -> None:
        """Replace the prefix lists the profile's prefix_list_mode applies to."""
        self._client.put(f"/ddos-mitigation/profiles/{network}/prefix-lists", json={"uuids": uuids})

    # ── Catalog ──────────────────────────────────────────────────

    def list_countries(self) -> list[DDoSCountry]:
        data: dict[str, Any] = self._client.get("/ddos-mitigation/countries")
        return [DDoSCountry.from_dict(c) for c in data.get("countries", [])]

    def list_asns(self, search: str | None = None) -> list[DDoSASN]:
        data: dict[str, Any] = self._client.get("/ddos-mitigation/asns", params={"search": search} if search else None)
        return [DDoSASN.from_dict(a) for a in data.get("asns", [])]

    # ── Prefix lists ─────────────────────────────────────────────

    def list_prefix_lists(self) -> list[DDoSPrefixList]:
        """The organization's prefix lists plus the global ones."""
        data: dict[str, Any] = self._client.get("/ddos-mitigation/prefix-lists")
        return [DDoSPrefixList.from_dict(p) for p in data.get("prefix_lists", [])]

    def create_prefix_list(self, name: str, description: str | None = None) -> None:
        """Create a prefix list. The API does not return it: find its uuid with list_prefix_lists."""
        body: dict[str, Any] = {"name": name}
        if description is not None:
            body["description"] = description
        self._client.post("/ddos-mitigation/prefix-lists", json=body)

    def delete_prefix_list(self, uuid: str) -> None:
        self._client.delete(f"/ddos-mitigation/prefix-lists/{uuid}")

    def list_prefix_list_entries(self, uuid: str) -> list[str]:
        """Networks of a prefix list, in CIDR notation."""
        data: list[dict[str, Any]] = self._client.get(f"/ddos-mitigation/prefix-lists/{uuid}/entries")
        return [e.get("network", "") for e in data]

    def add_prefix_list_entry(self, uuid: str, network: str) -> None:
        """Add an IP or CIDR (stored as a CIDR, 1.2.3.4 becomes 1.2.3.4/32). At most 100 entries."""
        self._client.post(f"/ddos-mitigation/prefix-lists/{uuid}/entries", json={"network": network})

    def delete_prefix_list_entry(self, uuid: str, network: str) -> None:
        self._client.delete(f"/ddos-mitigation/prefix-lists/{uuid}/entries/{network}")

    # ── Firewall rules ───────────────────────────────────────────

    def list_firewall_rules(self, network: str) -> list[DDoSFirewallRule]:
        data: dict[str, Any] = self._client.get(f"/ddos-mitigation/firewall-rules/{network}")
        return [DDoSFirewallRule.from_dict(r) for r in data.get("rules", [])]

    def create_firewall_rule(self, req: CreateDDoSFirewallRuleRequest) -> None:
        """Create a rule. The API does not return it: find its id with list_firewall_rules."""
        self._client.post("/ddos-mitigation/firewall-rules", json=req.to_dict())

    def delete_firewall_rule(self, rule_id: int | str) -> None:
        self._client.delete(f"/ddos-mitigation/firewall-rules/{rule_id}")

    def delete_firewall_rules(self, network: str, protocol: int, dst_port: int) -> None:
        """Delete the rules matching network, protocol and port, for instance every rule a subnet created."""
        self._client.delete(
            "/ddos-mitigation/firewall-rules/bulk",
            params={"network": network, "protocol": protocol, "dst_port": dst_port},
        )

    # ── Traffic capture ──────────────────────────────────────────

    def list_capture_ips(self) -> list[DDoSCaptureIP]:
        """Premium IPs whose traffic can be captured."""
        data: dict[str, Any] = self._client.get("/ddos-mitigation/traffic-capture/protected-ips")
        return [DDoSCaptureIP.from_dict(i) for i in data.get("ips", [])]

    def capture_traffic(self, req: DDoSTrafficCaptureRequest) -> DDoSTrafficCapture:
        """Sampled packets sent to one of your Premium IPs, with the action the scrubbers took."""
        data: dict[str, Any] = self._client.post("/ddos-mitigation/traffic-capture", json=req.to_dict())
        return DDoSTrafficCapture.from_dict(data)

    def get_traffic_stats(self, req: DDoSTrafficStatsRequest) -> DDoSTrafficStats:
        data: dict[str, Any] = self._client.post("/ddos-mitigation/traffic-capture/stats", json=req.to_dict())
        return DDoSTrafficStats.from_dict(data)
