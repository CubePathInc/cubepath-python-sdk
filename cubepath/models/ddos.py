from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

__all__ = [
    "DDoSAttack",
    "DDoSProtectedIP",
    "DDoSSubnetIP",
    "DDoSProtectedSubnet",
    "DDoSIPList",
    "DDoSProtectionProfile",
    "UpdateDDoSProtectionProfileRequest",
    "DDoSCountry",
    "DDoSASN",
    "DDoSPrefixList",
    "DDoSFirewallRule",
    "CreateDDoSFirewallRuleRequest",
    "DDoSCaptureIP",
    "DDoSTrafficCaptureRequest",
    "DDoSTrafficLog",
    "DDoSTrafficCapture",
    "DDoSTrafficStatsRequest",
    "DDoSTrafficStatsBucket",
    "DDoSTrafficStats",
]


def _simple(cls: Any, data: dict[str, Any] | None) -> Any:
    data = data or {}
    return cls(
        **{
            k: data.get(k, f.default_factory() if callable(f.default_factory) else f.default)
            for k, f in cls.__dataclass_fields__.items()
        }
    )


@dataclass
class DDoSAttack:
    attack_id: str = ""
    ip_address: str = ""
    start_time: str = ""
    duration: int = 0
    packets_second_peak: int = 0
    bytes_second_peak: int = 0
    """Deprecated: not returned by the API, always 0. Use gbps_peak."""
    gbps_peak: float = 0.0
    status: str = ""
    description: str = ""

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> DDoSAttack:
        return cls(**{k: data.get(k, f.default) for k, f in cls.__dataclass_fields__.items()})


# ── Protected IPs ────────────────────────────────────────────────


@dataclass
class DDoSProtectedIP:
    network: str = ""
    ip_type: str = ""
    protection_type: str = ""
    """Premium or Premium Always-On."""
    location_name: str | None = None
    location_description: str | None = None
    has_profile: bool = False
    firewall_rules_count: int = 0

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> DDoSProtectedIP:
        result: DDoSProtectedIP = _simple(cls, data)
        return result


@dataclass
class DDoSSubnetIP:
    address: str = ""
    has_profile: bool = False
    firewall_rules_count: int = 0

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> DDoSSubnetIP:
        result: DDoSSubnetIP = _simple(cls, data)
        return result


@dataclass
class DDoSProtectedSubnet(DDoSProtectedIP):
    prefix: int = 0
    ip_addresses: list[DDoSSubnetIP] = field(default_factory=list)
    """IPv4 subnets only; IPv6 subnets are not expanded."""

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> DDoSProtectedSubnet:
        result: DDoSProtectedSubnet = _simple(cls, data)
        result.ip_addresses = [DDoSSubnetIP.from_dict(i) for i in data.get("ip_addresses", [])]
        return result


@dataclass
class DDoSIPList:
    single_ips: list[DDoSProtectedIP] = field(default_factory=list)
    subnets: list[DDoSProtectedSubnet] = field(default_factory=list)
    total: int = 0

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> DDoSIPList:
        return cls(
            single_ips=[DDoSProtectedIP.from_dict(i) for i in data.get("single_ips", [])],
            subnets=[DDoSProtectedSubnet.from_dict(s) for s in data.get("subnets", [])],
            total=data.get("total", 0),
        )


# ── Protection profiles ──────────────────────────────────────────


@dataclass
class UpdateDDoSProtectionProfileRequest:
    """The whole profile: an update replaces every field, so unset fields go back to these defaults.

    Levels are 0-10. Modes are 0 off, 1 blacklist, 2 whitelist. default_action is 0 filter,
    1 accept, 2 drop. Rate limits must be at least 1.
    """

    tcp_validation_level: int = 1
    tcp_validation_sym_level: int = 0
    udp_validation_level: int = 0
    invalid_filter_level: int = 1
    fragmented_filter_level: int = 1
    amplification_udp_level: int = 1
    amplification_tcp_level: int = 1
    icmp_rate_limit_level: int = 0
    same_packet_size_level: int = 1
    stateful_firewall_level: int = 0
    default_action: int = 0
    country_mode: int = 0
    asn_mode: int = 0
    prefix_list_mode: int = 0
    udp_threshold_pps: int = 1000
    tcp_threshold_pps: int = 1000
    tcp_syn_threshold_pps: int = 10
    tcp_ack_threshold_pps: int = 200
    icmp_threshold_pps: int = 100
    udp_threshold_mbps: int = 100
    tcp_threshold_mbps: int = 100
    tcp_syn_threshold_mbps: int = 100
    tcp_ack_threshold_mbps: int = 100
    icmp_threshold_mbps: int = 100
    syn_flood_threshold: int = 0
    syn_flood_block_secs: int = 60
    always_on_mitigation: int | None = None
    """0 or 1; left unchanged when None."""
    symmetric_routing: int | None = None
    """0 or 1; left unchanged when None."""

    def to_dict(self) -> dict[str, Any]:
        d: dict[str, Any] = {
            k: getattr(self, k)
            for k in self.__dataclass_fields__
            if k not in ("always_on_mitigation", "symmetric_routing")
        }
        if self.always_on_mitigation is not None:
            d["always_on_mitigation"] = self.always_on_mitigation
        if self.symmetric_routing is not None:
            d["symmetric_routing"] = self.symmetric_routing
        return d


@dataclass
class DDoSProtectionProfile(UpdateDDoSProtectionProfileRequest):
    network: str = ""

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> DDoSProtectionProfile:
        result: DDoSProtectionProfile = _simple(cls, data)
        return result

    def to_request(self) -> UpdateDDoSProtectionProfileRequest:
        """The profile as an update request, to change a few fields and send it back."""
        fields = UpdateDDoSProtectionProfileRequest.__dataclass_fields__
        return UpdateDDoSProtectionProfileRequest(**{k: getattr(self, k) for k in fields})


# ── Catalog ──────────────────────────────────────────────────────


@dataclass
class DDoSCountry:
    iso_code: str = ""
    name: str | None = None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> DDoSCountry:
        result: DDoSCountry = _simple(cls, data)
        return result


@dataclass
class DDoSASN:
    asn: int = 0
    name: str | None = None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> DDoSASN:
        result: DDoSASN = _simple(cls, data)
        return result


@dataclass
class DDoSPrefixList:
    uuid: str = ""
    name: str = ""
    description: str | None = None
    is_global: bool = False
    created_at: str | None = None
    """Not returned for the prefix lists assigned to a profile."""
    entries_count: int = 0

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> DDoSPrefixList:
        result: DDoSPrefixList = _simple(cls, data)
        return result


# ── Firewall rules ───────────────────────────────────────────────


@dataclass
class DDoSFirewallRule:
    id: int = 0
    network: str = ""
    protocol: int = 0
    dst_port: int = 0
    action: int = 0
    action_label: str = ""
    tcp_syn: int = 0
    tcp_ack: int = 0
    tcp_synack: int = 0
    tcp_rst: int = 0
    tcp_fin: int = 0
    tcp_all: int = 0
    udp: int = 0
    icmp: int = 0

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> DDoSFirewallRule:
        result: DDoSFirewallRule = _simple(cls, data)
        return result


@dataclass
class CreateDDoSFirewallRuleRequest:
    """A rule for an IP or network you own. A subnet creates one rule per IP.

    protocol is 0 any, 1 ICMP, 6 TCP or 17 UDP; dst_port 0 means any. action is 0 drop,
    1 accept, 2 filter, or an application filter (10-12 FiveM TCP, 15-17 FiveM UDP, 20-21 RDP,
    30-31 DNS, 40 Minecraft Java, 50 TLS). Actions 60 (packets/s) and 61 (Mbps) rate limit each
    source IP with the per-type limits below.
    """

    network: str
    protocol: int
    dst_port: int
    action: int
    tcp_syn: int = 0
    tcp_ack: int = 0
    tcp_synack: int = 0
    tcp_rst: int = 0
    tcp_fin: int = 0
    tcp_all: int = 0
    udp: int = 0
    icmp: int = 0

    def to_dict(self) -> dict[str, Any]:
        return {k: getattr(self, k) for k in self.__dataclass_fields__}


# ── Traffic capture ──────────────────────────────────────────────


@dataclass
class DDoSCaptureIP:
    address: str = ""
    netmask: str | None = None
    network: str = ""
    location: str | None = None
    assigned_to: str | None = None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> DDoSCaptureIP:
        result: DDoSCaptureIP = _simple(cls, data)
        return result


@dataclass
class DDoSTrafficCaptureRequest:
    """Filters for the sampled packets sent to one of your IPs or subnets. Times are ISO 8601."""

    start_time: str
    end_time: str
    destination_ip: str
    include_src_ips: list[str] = field(default_factory=list)
    exclude_src_ips: list[str] = field(default_factory=list)
    include_src_ports: list[int] = field(default_factory=list)
    exclude_src_ports: list[int] = field(default_factory=list)
    include_dst_ports: list[int] = field(default_factory=list)
    exclude_dst_ports: list[int] = field(default_factory=list)
    min_src_port: int | None = None
    max_src_port: int | None = None
    min_dst_port: int | None = None
    max_dst_port: int | None = None
    include_protocols: list[str] = field(default_factory=list)
    exclude_protocols: list[str] = field(default_factory=list)
    include_actions: list[str] = field(default_factory=list)
    exclude_actions: list[str] = field(default_factory=list)
    include_tcp_flags: list[str] = field(default_factory=list)
    exclude_tcp_flags: list[str] = field(default_factory=list)
    min_packet_len: int | None = None
    max_packet_len: int | None = None
    min_ttl: int | None = None
    max_ttl: int | None = None
    has_payload: bool | None = None
    limit: int | None = None

    def to_dict(self) -> dict[str, Any]:
        d: dict[str, Any] = {}
        for k in self.__dataclass_fields__:
            v = getattr(self, k)
            if v is None or (isinstance(v, list) and not v):
                continue
            d[k] = v
        return d


@dataclass
class DDoSTrafficLog:
    timestamp: str = ""
    node: str | None = None
    src_ip: str = ""
    dst_ip: str = ""
    src_port: int = 0
    dst_port: int = 0
    protocol: str = ""
    action: str = ""
    mitigation_name: str | None = None
    is_drop: bool = False
    packet_len: int = 0
    ttl: int = 0
    sample_rate: int | None = None
    tcp_flags: str | None = None
    icmp_type: int | None = None
    icmp_code: int | None = None
    src_country: str | None = None
    payload_len: int | None = None
    payload: str | None = None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> DDoSTrafficLog:
        result: DDoSTrafficLog = _simple(cls, data)
        return result


@dataclass
class DDoSTrafficCapture:
    start_time: str = ""
    end_time: str = ""
    total_logs: int = 0
    logs: list[DDoSTrafficLog] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> DDoSTrafficCapture:
        result: DDoSTrafficCapture = _simple(cls, data)
        result.logs = [DDoSTrafficLog.from_dict(entry) for entry in data.get("logs", [])]
        return result


@dataclass
class DDoSTrafficStatsRequest:
    """Passed and dropped traffic over time. Times are ISO 8601; interval is 10s, 30s, 1m, 5m, 15m or 1h."""

    start_time: str
    end_time: str
    destination_ips: list[str] = field(default_factory=list)
    """Empty means every protected IP of the organization."""
    interval: str = "1m"

    def to_dict(self) -> dict[str, Any]:
        return {
            "start_time": self.start_time,
            "end_time": self.end_time,
            "destination_ips": self.destination_ips,
            "interval": self.interval,
        }


@dataclass
class DDoSTrafficStatsBucket:
    timestamp: str = ""
    pass_count: int = 0
    drop_count: int = 0
    pass_bytes: int = 0
    drop_bytes: int = 0
    pass_pps: float = 0.0
    drop_pps: float = 0.0

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> DDoSTrafficStatsBucket:
        result: DDoSTrafficStatsBucket = _simple(cls, data)
        return result


@dataclass
class DDoSTrafficStats:
    start_time: str = ""
    end_time: str = ""
    interval: str = ""
    total_pass: int = 0
    total_drop: int = 0
    buckets: list[DDoSTrafficStatsBucket] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> DDoSTrafficStats:
        result: DDoSTrafficStats = _simple(cls, data)
        result.buckets = [DDoSTrafficStatsBucket.from_dict(b) for b in data.get("buckets", [])]
        return result
