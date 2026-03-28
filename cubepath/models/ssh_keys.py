from __future__ import annotations

from dataclasses import dataclass
from typing import Any

__all__ = ["SSHKey", "CreateSSHKeyRequest"]


@dataclass
class SSHKey:
    id: str = ""
    name: str = ""
    ssh_key: str = ""
    fingerprint: str = ""
    key_type: str = ""
    created_at: str = ""

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> SSHKey:
        return cls(
            id=data.get("id", ""),
            name=data.get("name", ""),
            ssh_key=data.get("ssh_key", ""),
            fingerprint=data.get("fingerprint", ""),
            key_type=data.get("key_type", ""),
            created_at=data.get("created_at", ""),
        )


@dataclass
class CreateSSHKeyRequest:
    name: str
    ssh_key: str

    def to_dict(self) -> dict[str, Any]:
        return {"name": self.name, "ssh_key": self.ssh_key}
