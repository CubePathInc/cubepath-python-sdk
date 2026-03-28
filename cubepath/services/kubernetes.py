from __future__ import annotations

from typing import TYPE_CHECKING, Any

from cubepath.models.kubernetes import (
    CreateKubernetesClusterRequest,
    CreateNodePoolRequest,
    InstallAddonRequest,
    InstalledAddon,
    KubernetesAddon,
    KubernetesCluster,
    KubernetesClusterResponse,
    KubernetesLB,
    KubernetesPlan,
    KubernetesVersion,
    NodePool,
    NodePoolResponse,
    UpdateKubernetesClusterRequest,
    UpdateNodePoolRequest,
)

if TYPE_CHECKING:
    from cubepath.client import CubePathClient


class KubernetesService:
    def __init__(self, client: CubePathClient) -> None:
        self._client = client

    # ── Clusters ─────────────────────────────────────────────────

    def list_versions(self) -> list[KubernetesVersion]:
        data: list[dict[str, Any]] = self._client.get("/kubernetes/versions")
        return [KubernetesVersion.from_dict(v) for v in data]

    def list_plans(self, version: str) -> list[KubernetesPlan]:
        data: list[dict[str, Any]] = self._client.get("/kubernetes/plans", params={"version": version})
        return [KubernetesPlan.from_dict(p) for p in data]

    def list(self) -> list[KubernetesCluster]:
        data: list[dict[str, Any]] = self._client.get("/kubernetes/")
        return [KubernetesCluster.from_dict(c) for c in data]

    def get(self, cluster_uuid: str) -> KubernetesCluster:
        data: dict[str, Any] = self._client.get(f"/kubernetes/{cluster_uuid}")
        return KubernetesCluster.from_dict(data)

    def create(self, req: CreateKubernetesClusterRequest) -> KubernetesClusterResponse:
        data: dict[str, Any] = self._client.post("/kubernetes/", json=req.to_dict())
        return KubernetesClusterResponse.from_dict(data)

    def update(self, cluster_uuid: str, req: UpdateKubernetesClusterRequest) -> None:
        self._client.patch(f"/kubernetes/{cluster_uuid}", json=req.to_dict())

    def delete(self, cluster_uuid: str) -> None:
        self._client.delete(f"/kubernetes/{cluster_uuid}")

    def get_kubeconfig(self, cluster_uuid: str) -> str:
        data: bytes = self._client.get_raw(f"/kubernetes/{cluster_uuid}/kubeconfig")
        return data.decode()

    def move(self, cluster_uuid: str, project_id: str) -> None:
        self._client.post(f"/kubernetes/{cluster_uuid}/move", json={"project_id": project_id})

    def list_load_balancers(self, cluster_uuid: str) -> list[KubernetesLB]:
        data: list[dict[str, Any]] = self._client.get(f"/kubernetes/{cluster_uuid}/loadbalancers")
        return [KubernetesLB.from_dict(lb) for lb in data]

    # ── Node Pools ───────────────────────────────────────────────

    def list_node_pools(self, cluster_uuid: str) -> list[NodePool]:
        data: list[dict[str, Any]] = self._client.get(f"/kubernetes/{cluster_uuid}/node-pools/")
        return [NodePool.from_dict(np) for np in data]

    def create_node_pool(self, cluster_uuid: str, req: CreateNodePoolRequest) -> NodePoolResponse:
        data: dict[str, Any] = self._client.post(
            f"/kubernetes/{cluster_uuid}/node-pools/",
            json=req.to_dict(),
        )
        return NodePoolResponse.from_dict(data)

    def update_node_pool(self, cluster_uuid: str, pool_uuid: str, req: UpdateNodePoolRequest) -> None:
        self._client.patch(f"/kubernetes/{cluster_uuid}/node-pools/{pool_uuid}", json=req.to_dict())

    def delete_node_pool(self, cluster_uuid: str, pool_uuid: str) -> None:
        self._client.delete(f"/kubernetes/{cluster_uuid}/node-pools/{pool_uuid}")

    def add_nodes(self, cluster_uuid: str, pool_uuid: str, count: int) -> None:
        self._client.post(
            f"/kubernetes/{cluster_uuid}/node-pools/{pool_uuid}/nodes",
            json={"count": count},
        )

    def remove_node(self, cluster_uuid: str, pool_uuid: str, vps_id: str) -> None:
        self._client.delete(f"/kubernetes/{cluster_uuid}/node-pools/{pool_uuid}/nodes/{vps_id}")

    # ── Addons ───────────────────────────────────────────────────

    def list_available_addons(self) -> list[KubernetesAddon]:
        data: list[dict[str, Any]] = self._client.get("/kubernetes/addons")
        return [KubernetesAddon.from_dict(a) for a in data]

    def get_addon(self, slug: str) -> KubernetesAddon:
        data: dict[str, Any] = self._client.get(f"/kubernetes/addons/{slug}")
        return KubernetesAddon.from_dict(data)

    def list_installed_addons(self, cluster_uuid: str) -> list[InstalledAddon]:
        data: list[dict[str, Any]] = self._client.get(f"/kubernetes/{cluster_uuid}/addons")
        return [InstalledAddon.from_dict(a) for a in data]

    def install_addon(self, cluster_uuid: str, slug: str, req: InstallAddonRequest | None = None) -> None:
        self._client.post(
            f"/kubernetes/{cluster_uuid}/addons/{slug}/install",
            json=req.to_dict() if req else {},
        )

    def uninstall_addon(self, cluster_uuid: str, addon_uuid: str) -> None:
        self._client.delete(f"/kubernetes/{cluster_uuid}/addons/{addon_uuid}")
