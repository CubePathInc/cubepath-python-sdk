from __future__ import annotations

from typing import TYPE_CHECKING, Any

from cubepath.models.ssh_keys import CreateSSHKeyRequest, SSHKey

if TYPE_CHECKING:
    from cubepath.client import CubePathClient


class SSHKeyService:
    def __init__(self, client: CubePathClient) -> None:
        self._client = client

    def create(self, req: CreateSSHKeyRequest) -> SSHKey:
        data: dict[str, Any] = self._client.post("/sshkey/create", json=req.to_dict())
        return SSHKey.from_dict(data)

    def list(self) -> list[SSHKey]:
        data: Any = self._client.get("/sshkey/user/sshkeys")
        keys: list[dict[str, Any]] = data.get("sshkeys", []) if isinstance(data, dict) else data
        return [SSHKey.from_dict(k) for k in keys]

    def update(self, key_id: str, name: str) -> SSHKey:
        """Rename a key; the key itself cannot be changed."""
        data: dict[str, Any] = self._client.put(f"/sshkey/{key_id}", json={"name": name})
        return SSHKey.from_dict(data.get("sshkey", {}))

    def delete(self, key_id: str) -> None:
        self._client.delete(f"/sshkey/{key_id}")
