from __future__ import annotations

from dataclasses import dataclass
from typing import Any

__all__ = ["DDoSAttack"]


@dataclass
class DDoSAttack:
    attack_id: str = ""
    ip_address: str = ""
    start_time: str = ""
    duration: int = 0
    packets_second_peak: int = 0
    bytes_second_peak: int = 0
    status: str = ""
    description: str = ""

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> DDoSAttack:
        return cls(**{k: data.get(k, v) for k, v in cls.__dataclass_fields__.items()})
