from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

__all__ = [
    "Notificator",
    "CreateNotificatorRequest",
    "UpdateNotificatorRequest",
    "AlertActionRequest",
    "AlertAction",
    "AlertSummary",
    "Alert",
    "CreateAlertRequest",
    "UpdateAlertRequest",
    "AlertHistoryEntry",
]


def _simple(cls: Any, data: dict[str, Any] | None) -> Any:
    data = data or {}
    return cls(
        **{
            k: data.get(k, f.default_factory() if callable(f.default_factory) else f.default)
            for k, f in cls.__dataclass_fields__.items()
        }
    )


# ── Notification channels ────────────────────────────────────────


@dataclass
class Notificator:
    id: str = ""
    name: str = ""
    type: str = ""
    """slack, discord or email."""
    config: dict[str, Any] = field(default_factory=dict)
    """Slack and Discord webhook URLs are masked when read back."""
    enabled: bool = True
    created_at: str = ""
    updated_at: str = ""

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Notificator:
        result: Notificator = _simple(cls, data)
        return result


@dataclass
class CreateNotificatorRequest:
    name: str
    type: str
    """slack, discord or email."""
    config: dict[str, Any] = field(default_factory=dict)
    """{"webhook_url": "https://..."} for slack and discord; email needs none (the account email is used)."""
    enabled: bool = True

    def to_dict(self) -> dict[str, Any]:
        return {"name": self.name, "type": self.type, "config": self.config, "enabled": self.enabled}


@dataclass
class UpdateNotificatorRequest:
    name: str | None = None
    config: dict[str, Any] | None = None
    enabled: bool | None = None

    def to_dict(self) -> dict[str, Any]:
        d: dict[str, Any] = {}
        if self.name is not None:
            d["name"] = self.name
        if self.config is not None:
            d["config"] = self.config
        if self.enabled is not None:
            d["enabled"] = self.enabled
        return d


# ── Alerts ───────────────────────────────────────────────────────


@dataclass
class AlertActionRequest:
    action_type: str
    """notify (needs notificator_id), destroy_vps or create_vps (needs config)."""
    notificator_id: str | None = None
    config: dict[str, Any] | None = None
    """For create_vps: name, template_name, plan_name and location_name."""
    order: int = 0
    enabled: bool = True

    def to_dict(self) -> dict[str, Any]:
        d: dict[str, Any] = {"action_type": self.action_type, "order": self.order, "enabled": self.enabled}
        if self.notificator_id is not None:
            d["notificator_id"] = self.notificator_id
        if self.config is not None:
            d["config"] = self.config
        return d


@dataclass
class AlertAction:
    id: str = ""
    action_type: str = ""
    notificator_id: str | None = None
    config: dict[str, Any] | None = None
    order: int = 0
    enabled: bool = True
    created_at: str = ""

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> AlertAction:
        result: AlertAction = _simple(cls, data)
        return result


@dataclass
class AlertSummary:
    id: str = ""
    project_id: int = 0
    name: str = ""
    description: str | None = None
    target_type: str = ""
    """vps, baremetal or availability_group."""
    target_id: str = ""
    metric_type: str = ""
    """cpu, ram, disk, network_in or network_out."""
    operator: str = ""
    """gt, lt, gte, lte or eq."""
    threshold: float = 0.0
    status: str = ""
    """enabled, disabled, triggered or resolved."""
    actions_count: int = 0
    created_at: str = ""

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> AlertSummary:
        result: AlertSummary = _simple(cls, data)
        return result


@dataclass
class Alert:
    id: str = ""
    project_id: int = 0
    name: str = ""
    description: str | None = None
    target_type: str = ""
    target_id: str = ""
    metric_type: str = ""
    operator: str = ""
    threshold: float = 0.0
    duration_seconds: int = 0
    cooldown_seconds: int = 0
    status: str = ""
    last_triggered_at: str | None = None
    last_resolved_at: str | None = None
    created_at: str = ""
    updated_at: str = ""
    actions: list[AlertAction] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Alert:
        result: Alert = _simple(cls, data)
        result.actions = [AlertAction.from_dict(a) for a in data.get("actions", [])]
        return result


@dataclass
class CreateAlertRequest:
    project_id: int
    name: str
    target_type: str
    """vps, baremetal or availability_group."""
    target_id: str
    """VPS id, baremetal id or availability group uuid."""
    metric_type: str
    """cpu, ram, disk, network_in or network_out (baremetal: network only)."""
    operator: str
    """gt, lt, gte, lte or eq."""
    threshold: float
    actions: list[AlertActionRequest]
    description: str | None = None
    duration_seconds: int = 300
    """How long the condition must hold before the alert fires."""
    cooldown_seconds: int = 600

    def to_dict(self) -> dict[str, Any]:
        d: dict[str, Any] = {
            "project_id": self.project_id,
            "name": self.name,
            "target_type": self.target_type,
            "target_id": self.target_id,
            "metric_type": self.metric_type,
            "operator": self.operator,
            "threshold": self.threshold,
            "duration_seconds": self.duration_seconds,
            "cooldown_seconds": self.cooldown_seconds,
            "actions": [a.to_dict() for a in self.actions],
        }
        if self.description is not None:
            d["description"] = self.description
        return d


@dataclass
class UpdateAlertRequest:
    name: str | None = None
    description: str | None = None
    target_type: str | None = None
    target_id: str | None = None
    metric_type: str | None = None
    operator: str | None = None
    threshold: float | None = None
    duration_seconds: int | None = None
    cooldown_seconds: int | None = None
    status: str | None = None
    """enabled or disabled."""
    actions: list[AlertActionRequest] | None = None
    """Replaces every action when set."""

    def to_dict(self) -> dict[str, Any]:
        d: dict[str, Any] = {}
        for k in self.__dataclass_fields__:
            v = getattr(self, k)
            if v is None:
                continue
            d[k] = [a.to_dict() for a in v] if k == "actions" else v
        return d


@dataclass
class AlertHistoryEntry:
    id: str = ""
    trigger_id: str = ""
    event_type: str = ""
    metric_value: float | None = None
    details: dict[str, Any] | None = None
    created_at: str = ""

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> AlertHistoryEntry:
        result: AlertHistoryEntry = _simple(cls, data)
        return result
