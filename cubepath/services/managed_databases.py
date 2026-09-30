from __future__ import annotations

import builtins
from typing import TYPE_CHECKING, Any

from cubepath.models.managed_databases import (
    CreateManagedDatabaseRequest,
    CreateManagedDatabaseResponse,
    CreateManagedDatabaseUserRequest,
    CreateManagedDatabaseUserResponse,
    LogicalDatabase,
    ManagedDatabase,
    ManagedDatabaseConfig,
    ManagedDatabaseConfigUpdateResponse,
    ManagedDatabaseCredentials,
    ManagedDatabaseDetail,
    ManagedDatabaseLocationPlans,
    ManagedDatabaseMetrics,
    ManagedDatabaseScaleResponse,
    ManagedDatabaseUser,
    UpdateManagedDatabaseRequest,
)

if TYPE_CHECKING:
    from cubepath.client import CubePathClient


class ManagedDatabaseService:
    """Managed MySQL, Valkey and PostgreSQL: instances, scaling, configuration, databases and users."""

    def __init__(self, client: CubePathClient) -> None:
        self._client = client

    # ── Plans ────────────────────────────────────────────────────

    def list_plans(self, engine: str | None = None) -> list[ManagedDatabaseLocationPlans]:
        """Plans grouped by location. The plan picks the location a database is deployed in."""
        data: list[dict[str, Any]] = self._client.get(
            "/managed-database-plans/", params={"engine": engine} if engine else None
        )
        return [ManagedDatabaseLocationPlans.from_dict(lp) for lp in data]

    # ── Instances ────────────────────────────────────────────────

    def list(self) -> list[ManagedDatabase]:
        data: list[dict[str, Any]] = self._client.get("/managed-databases/")
        return [ManagedDatabase.from_dict(md) for md in data]

    def get(self, md_uuid: str) -> ManagedDatabaseDetail:
        data: dict[str, Any] = self._client.get(f"/managed-databases/{md_uuid}")
        return ManagedDatabaseDetail.from_dict(data)

    def create(self, req: CreateManagedDatabaseRequest) -> CreateManagedDatabaseResponse:
        """Create a database asynchronously: it is usable once its status is "active".

        Only one creation per organization runs at a time; a 409 means retry shortly.
        """
        data: dict[str, Any] = self._client.post("/managed-databases/", json=req.to_dict())
        return CreateManagedDatabaseResponse.from_dict(data)

    def update(self, md_uuid: str, req: UpdateManagedDatabaseRequest) -> None:
        """Change the name, label or backup policy."""
        self._client.patch(f"/managed-databases/{md_uuid}", json=req.to_dict())

    def delete(self, md_uuid: str) -> None:
        """Delete a database and all its data, asynchronously. Not allowed while it is provisioning."""
        self._client.delete(f"/managed-databases/{md_uuid}")

    def configure_protection(self, md_uuid: str, enabled: bool) -> None:
        """A protected database cannot be deleted."""
        self._client.post(f"/managed-databases/{md_uuid}/protection", json={"enabled": enabled})

    # ── Operations ───────────────────────────────────────────────

    def scale(
        self, md_uuid: str, *, replicas: int | None = None, plan_uuid: str | None = None
    ) -> ManagedDatabaseScaleResponse:
        """Change the number of replicas or move to another plan (exactly one of the two)."""
        if (replicas is None) == (plan_uuid is None):
            raise ValueError("provide exactly one of replicas or plan_uuid")
        body: dict[str, Any] = {"replicas": replicas} if replicas is not None else {"plan_uuid": plan_uuid}
        data: dict[str, Any] = self._client.post(f"/managed-databases/{md_uuid}/scale", json=body)
        return ManagedDatabaseScaleResponse.from_dict(data)

    def get_credentials(self, md_uuid: str) -> ManagedDatabaseCredentials:
        """Connection credentials of the admin user."""
        data: dict[str, Any] = self._client.get(f"/managed-databases/{md_uuid}/credentials")
        return ManagedDatabaseCredentials.from_dict(data)

    def rotate_credentials(self, md_uuid: str) -> None:
        """Generate a new admin password in the background; read it with get_credentials."""
        self._client.post(f"/managed-databases/{md_uuid}/credentials/rotate")

    def get_config(self, md_uuid: str) -> ManagedDatabaseConfig:
        data: dict[str, Any] = self._client.get(f"/managed-databases/{md_uuid}/config")
        return ManagedDatabaseConfig.from_dict(data)

    def update_config(
        self, md_uuid: str, params: dict[str, int | float | str | bool]
    ) -> ManagedDatabaseConfigUpdateResponse:
        """Change tunable parameters; the response lists those that need a rolling restart."""
        data: dict[str, Any] = self._client.patch(f"/managed-databases/{md_uuid}/config", json={"params": params})
        return ManagedDatabaseConfigUpdateResponse.from_dict(data)

    def get_metrics(
        self, md_uuid: str, *, metrics: builtins.list[str] | None = None, time_range: str | None = None
    ) -> ManagedDatabaseMetrics:
        """Metrics among connections, cpu, memory and replication_lag; time_range like 1h, 24h, 7d or 30d."""
        params: dict[str, Any] = {}
        if metrics:
            params["metrics"] = ",".join(metrics)
        if time_range:
            params["time_range"] = time_range
        data: dict[str, Any] = self._client.get(f"/managed-databases/{md_uuid}/metrics", params=params or None)
        return ManagedDatabaseMetrics.from_dict(data)

    # ── Logical databases ────────────────────────────────────────

    def list_databases(self, md_uuid: str) -> builtins.list[LogicalDatabase]:
        data: list[dict[str, Any]] = self._client.get(f"/managed-databases/{md_uuid}/databases")
        return [LogicalDatabase.from_dict(d) for d in data]

    def create_database(self, md_uuid: str, name: str) -> LogicalDatabase:
        """Create a logical database in the background. Not available for Valkey."""
        data: dict[str, Any] = self._client.post(f"/managed-databases/{md_uuid}/databases", json={"name": name})
        return LogicalDatabase.from_dict(data)

    def delete_database(self, md_uuid: str, db_uuid: str) -> None:
        self._client.delete(f"/managed-databases/{md_uuid}/databases/{db_uuid}")

    # ── Users ────────────────────────────────────────────────────

    def list_users(self, md_uuid: str) -> builtins.list[ManagedDatabaseUser]:
        data: list[dict[str, Any]] = self._client.get(f"/managed-databases/{md_uuid}/users")
        return [ManagedDatabaseUser.from_dict(u) for u in data]

    def create_user(self, md_uuid: str, req: CreateManagedDatabaseUserRequest) -> CreateManagedDatabaseUserResponse:
        """Create a user in the background. The password is only returned here."""
        data: dict[str, Any] = self._client.post(f"/managed-databases/{md_uuid}/users", json=req.to_dict())
        return CreateManagedDatabaseUserResponse.from_dict(data)

    def delete_user(self, md_uuid: str, user_uuid: str) -> None:
        self._client.delete(f"/managed-databases/{md_uuid}/users/{user_uuid}")
