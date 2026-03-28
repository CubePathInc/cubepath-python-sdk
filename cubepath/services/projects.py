from __future__ import annotations

from typing import TYPE_CHECKING, Any

from cubepath.models.projects import CreateProjectRequest, Project, ProjectResponse

if TYPE_CHECKING:
    from cubepath.client import CubePathClient


class ProjectService:
    def __init__(self, client: CubePathClient) -> None:
        self._client = client

    def create(self, req: CreateProjectRequest) -> Project:
        data: dict[str, Any] = self._client.post("/projects/", json=req.to_dict())
        return Project.from_dict(data)

    def list(self) -> list[ProjectResponse]:
        data: list[dict[str, Any]] = self._client.get("/projects/")
        return [ProjectResponse.from_dict(p) for p in data]

    def get(self, project_id: str) -> ProjectResponse:
        projects = self.list()
        for p in projects:
            if p.project.id == project_id:
                return p
        from cubepath.exceptions import APIError

        raise APIError(404, "Not Found", f"project {project_id} not found")

    def delete(self, project_id: str) -> None:
        self._client.delete(f"/projects/{project_id}")
