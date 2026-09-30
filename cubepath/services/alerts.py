from __future__ import annotations

import builtins
from typing import TYPE_CHECKING, Any

from cubepath.models.alerts import (
    Alert,
    AlertHistoryEntry,
    AlertSummary,
    CreateAlertRequest,
    CreateNotificatorRequest,
    Notificator,
    UpdateAlertRequest,
    UpdateNotificatorRequest,
)

if TYPE_CHECKING:
    from cubepath.client import CubePathClient


class AlertService:
    """Cloud Alerts: metric alerts on servers and the notification channels they notify."""

    def __init__(self, client: CubePathClient) -> None:
        self._client = client

    # ── Notification channels ────────────────────────────────────

    def list_notificators(self) -> list[Notificator]:
        data: list[dict[str, Any]] = self._client.get("/triggers/notificators/")
        return [Notificator.from_dict(n) for n in data]

    def get_notificator(self, notificator_id: str) -> Notificator:
        data: dict[str, Any] = self._client.get(f"/triggers/notificators/{notificator_id}")
        return Notificator.from_dict(data)

    def create_notificator(self, req: CreateNotificatorRequest) -> Notificator:
        data: dict[str, Any] = self._client.post("/triggers/notificators/", json=req.to_dict())
        return Notificator.from_dict(data)

    def update_notificator(self, notificator_id: str, req: UpdateNotificatorRequest) -> Notificator:
        data: dict[str, Any] = self._client.put(f"/triggers/notificators/{notificator_id}", json=req.to_dict())
        return Notificator.from_dict(data)

    def delete_notificator(self, notificator_id: str) -> None:
        self._client.delete(f"/triggers/notificators/{notificator_id}")

    # ── Alerts ───────────────────────────────────────────────────

    def list(self, *, project_id: int | None = None, status: str | None = None) -> list[AlertSummary]:
        params: dict[str, Any] = {}
        if project_id is not None:
            params["project_id"] = project_id
        if status:
            params["status"] = status
        data: list[dict[str, Any]] = self._client.get("/triggers/", params=params or None)
        return [AlertSummary.from_dict(a) for a in data]

    def get(self, alert_id: str) -> Alert:
        data: dict[str, Any] = self._client.get(f"/triggers/{alert_id}")
        return Alert.from_dict(data)

    def create(self, req: CreateAlertRequest) -> Alert:
        data: dict[str, Any] = self._client.post("/triggers/", json=req.to_dict())
        return Alert.from_dict(data)

    def update(self, alert_id: str, req: UpdateAlertRequest) -> Alert:
        data: dict[str, Any] = self._client.put(f"/triggers/{alert_id}", json=req.to_dict())
        return Alert.from_dict(data)

    def delete(self, alert_id: str) -> None:
        self._client.delete(f"/triggers/{alert_id}")

    def history(self, alert_id: str, limit: int = 50) -> builtins.list[AlertHistoryEntry]:
        """Latest events of an alert (fired, resolved...), at most 200."""
        data: list[dict[str, Any]] = self._client.get(f"/triggers/{alert_id}/history", params={"limit": limit})
        return [AlertHistoryEntry.from_dict(h) for h in data]
