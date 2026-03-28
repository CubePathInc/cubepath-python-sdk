from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

__all__ = [
    "KubernetesVersion",
    "KubernetesPlan",
    "KubernetesCluster",
    "KubernetesLocation",
    "KubernetesNetwork",
    "NodePool",
    "NodePoolPlan",
    "Node",
    "NodeTaint",
    "KubernetesAddon",
    "InstalledAddon",
    "KubernetesLB",
    "KubernetesClusterResponse",
    "NodePoolResponse",
    "CreateKubernetesClusterRequest",
    "CreateNodePoolConfig",
    "ClusterNetworkConfig",
    "UpdateKubernetesClusterRequest",
    "CreateNodePoolRequest",
    "UpdateNodePoolRequest",
    "InstallAddonRequest",
]


@dataclass
class KubernetesVersion:
    version: str = ""
    is_default: bool = False
    min_cpu: int = 0
    min_ram_mb: int = 0

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> KubernetesVersion:
        return cls(**{k: data.get(k, f.default) for k, f in cls.__dataclass_fields__.items()})


@dataclass
class KubernetesPlan:
    id: str = ""
    name: str = ""
    cpu: int = 0
    ram: int = 0
    storage: int = 0
    price_per_hour: str = ""

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> KubernetesPlan:
        return cls(**{k: data.get(k, f.default) for k, f in cls.__dataclass_fields__.items()})


@dataclass
class KubernetesLocation:
    location_name: str = ""
    description: str = ""

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> KubernetesLocation:
        return cls(**{k: data.get(k, f.default) for k, f in cls.__dataclass_fields__.items()})


@dataclass
class KubernetesNetwork:
    name: str = ""
    ip_range: str = ""
    prefix: int = 0

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> KubernetesNetwork:
        return cls(**{k: data.get(k, f.default) for k, f in cls.__dataclass_fields__.items()})


@dataclass
class NodePoolPlan:
    name: str = ""

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> NodePoolPlan:
        return cls(name=data.get("name", ""))


@dataclass
class Node:
    vps_name: str = ""
    vps_status: str = ""
    k8s_status: str = ""
    floating_ip: str = ""
    private_ip: str = ""

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Node:
        return cls(**{k: data.get(k, f.default) for k, f in cls.__dataclass_fields__.items()})


@dataclass
class NodePool:
    uuid: str = ""
    name: str = ""
    desired_nodes: int = 0
    min_nodes: int = 0
    max_nodes: int = 0
    auto_scale: bool = False
    plan: NodePoolPlan | None = None
    nodes: list[Node] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> NodePool:
        return cls(
            uuid=data.get("uuid", ""),
            name=data.get("name", ""),
            desired_nodes=data.get("desired_nodes", 0),
            min_nodes=data.get("min_nodes", 0),
            max_nodes=data.get("max_nodes", 0),
            auto_scale=data.get("auto_scale", False),
            plan=NodePoolPlan.from_dict(data["plan"]) if data.get("plan") else None,
            nodes=[Node.from_dict(n) for n in data.get("nodes", [])],
        )


@dataclass
class KubernetesCluster:
    uuid: str = ""
    name: str = ""
    label: str = ""
    status: str = ""
    version: str = ""
    ha_control_plane: bool = False
    api_endpoint: str = ""
    pod_cidr: str = ""
    service_cidr: str = ""
    billing_type: str = ""
    location: KubernetesLocation | None = None
    network: KubernetesNetwork | None = None
    node_pools: list[NodePool] = field(default_factory=list)
    worker_count: int = 0
    node_pool_count: int = 0
    created_at: str = ""

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> KubernetesCluster:
        return cls(
            uuid=data.get("uuid", ""),
            name=data.get("name", ""),
            label=data.get("label", ""),
            status=data.get("status", ""),
            version=data.get("version", ""),
            ha_control_plane=data.get("ha_control_plane", False),
            api_endpoint=data.get("api_endpoint", ""),
            pod_cidr=data.get("pod_cidr", ""),
            service_cidr=data.get("service_cidr", ""),
            billing_type=data.get("billing_type", ""),
            location=KubernetesLocation.from_dict(data["location"]) if data.get("location") else None,
            network=KubernetesNetwork.from_dict(data["network"]) if data.get("network") else None,
            node_pools=[NodePool.from_dict(np) for np in data.get("node_pools", [])],
            worker_count=data.get("worker_count", 0),
            node_pool_count=data.get("node_pool_count", 0),
            created_at=data.get("created_at", ""),
        )


@dataclass
class KubernetesAddon:
    name: str = ""
    slug: str = ""
    description: str = ""
    category: str = ""
    helm_repo_name: str = ""
    helm_repo_url: str = ""
    helm_chart: str = ""
    default_version: str = ""
    namespace: str = ""
    icon_url: str = ""
    documentation_url: str = ""
    keywords: list[str] = field(default_factory=list)
    min_k8s_version: str = ""

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> KubernetesAddon:
        return cls(**{k: data.get(k, f.default) for k, f in cls.__dataclass_fields__.items()})


@dataclass
class InstalledAddon:
    uuid: str = ""
    status: str = ""
    installed_version: str = ""
    addon: dict[str, str] = field(default_factory=dict)
    installed_at: str = ""

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> InstalledAddon:
        return cls(**{k: data.get(k, f.default) for k, f in cls.__dataclass_fields__.items()})


@dataclass
class KubernetesLB:
    uuid: str = ""
    name: str = ""
    status: str = ""
    floating_ip_address: str = ""

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> KubernetesLB:
        return cls(**{k: data.get(k, f.default) for k, f in cls.__dataclass_fields__.items()})


@dataclass
class KubernetesClusterResponse:
    detail: str = ""
    uuid: str = ""

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> KubernetesClusterResponse:
        return cls(**{k: data.get(k, f.default) for k, f in cls.__dataclass_fields__.items()})


@dataclass
class NodePoolResponse:
    detail: str = ""
    uuid: str = ""

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> NodePoolResponse:
        return cls(**{k: data.get(k, f.default) for k, f in cls.__dataclass_fields__.items()})


# ── Requests ─────────────────────────────────────────────────────


@dataclass
class ClusterNetworkConfig:
    network_id: str = ""
    node_cidr: str = ""
    pod_cidr: str = ""
    service_cidr: str = ""

    def to_dict(self) -> dict[str, Any]:
        d: dict[str, Any] = {}
        if self.network_id:
            d["network_id"] = self.network_id
        if self.node_cidr:
            d["node_cidr"] = self.node_cidr
        if self.pod_cidr:
            d["pod_cidr"] = self.pod_cidr
        if self.service_cidr:
            d["service_cidr"] = self.service_cidr
        return d


@dataclass
class CreateNodePoolConfig:
    name: str
    plan: str
    count: int

    def to_dict(self) -> dict[str, Any]:
        return {"name": self.name, "plan": self.plan, "count": self.count}


@dataclass
class NodeTaint:
    key: str
    value: str
    effect: str

    def to_dict(self) -> dict[str, Any]:
        return {"key": self.key, "value": self.value, "effect": self.effect}


@dataclass
class CreateKubernetesClusterRequest:
    project_id: str
    name: str
    location_name: str
    ha_control_plane: bool
    node_pools: list[CreateNodePoolConfig]
    version: str = ""
    network: ClusterNetworkConfig | None = None

    def to_dict(self) -> dict[str, Any]:
        d: dict[str, Any] = {
            "project_id": self.project_id,
            "name": self.name,
            "location_name": self.location_name,
            "ha_control_plane": self.ha_control_plane,
            "node_pools": [np.to_dict() for np in self.node_pools],
        }
        if self.version:
            d["version"] = self.version
        if self.network:
            d["network"] = self.network.to_dict()
        return d


@dataclass
class UpdateKubernetesClusterRequest:
    name: str = ""
    label: str = ""

    def to_dict(self) -> dict[str, Any]:
        d: dict[str, Any] = {}
        if self.name:
            d["name"] = self.name
        if self.label:
            d["label"] = self.label
        return d


@dataclass
class CreateNodePoolRequest:
    name: str
    plan: str
    count: int
    auto_scale: bool = False
    labels: dict[str, str] | None = None
    taints: list[NodeTaint] | None = None

    def to_dict(self) -> dict[str, Any]:
        d: dict[str, Any] = {
            "name": self.name,
            "plan": self.plan,
            "count": self.count,
            "auto_scale": self.auto_scale,
        }
        if self.labels:
            d["labels"] = self.labels
        if self.taints:
            d["taints"] = [t.to_dict() for t in self.taints]
        return d


@dataclass
class UpdateNodePoolRequest:
    name: str = ""
    desired_nodes: int | None = None
    min_nodes: int | None = None
    max_nodes: int | None = None
    auto_scale: bool | None = None
    labels: dict[str, str] | None = None
    taints: list[NodeTaint] | None = None

    def to_dict(self) -> dict[str, Any]:
        d: dict[str, Any] = {}
        if self.name:
            d["name"] = self.name
        if self.desired_nodes is not None:
            d["desired_nodes"] = self.desired_nodes
        if self.min_nodes is not None:
            d["min_nodes"] = self.min_nodes
        if self.max_nodes is not None:
            d["max_nodes"] = self.max_nodes
        if self.auto_scale is not None:
            d["auto_scale"] = self.auto_scale
        if self.labels is not None:
            d["labels"] = self.labels
        if self.taints is not None:
            d["taints"] = [t.to_dict() for t in self.taints]
        return d


@dataclass
class InstallAddonRequest:
    custom_values: dict[str, Any] | None = None

    def to_dict(self) -> dict[str, Any]:
        d: dict[str, Any] = {}
        if self.custom_values:
            d["custom_values"] = self.custom_values
        return d
