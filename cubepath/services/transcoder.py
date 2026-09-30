from __future__ import annotations

from typing import TYPE_CHECKING, Any

from cubepath.models.transcoder import (
    CreateTranscoderBatchRequest,
    CreateTranscoderJobRequest,
    TranscoderBatch,
    TranscoderJob,
    TranscoderJobList,
    TranscoderJobOutputs,
)

if TYPE_CHECKING:
    from cubepath.client import CubePathClient


class TranscoderService:
    """Video transcoding jobs from a URL or an S3 compatible bucket into your own bucket."""

    def __init__(self, client: CubePathClient) -> None:
        self._client = client

    def create_job(self, req: CreateTranscoderJobRequest) -> TranscoderJob:
        """Queue a job; follow it with get_job (or a webhook_url) until it is completed or failed."""
        data: dict[str, Any] = self._client.post("/transcoder/jobs", json=req.to_dict())
        return TranscoderJob.from_dict(data)

    def create_batch(self, req: CreateTranscoderBatchRequest) -> TranscoderBatch:
        """Queue up to 1000 jobs sharing the same outputs. All or nothing."""
        data: dict[str, Any] = self._client.post("/transcoder/jobs/batch", json=req.to_dict())
        return TranscoderBatch.from_dict(data)

    def list_jobs(self, *, batch_id: str | None = None, limit: int = 100, offset: int = 0) -> TranscoderJobList:
        """Jobs newest first. There is no total: page until fewer than limit jobs come back (limit max 500)."""
        params: dict[str, Any] = {"limit": limit, "offset": offset}
        if batch_id:
            params["batch_id"] = batch_id
        data: dict[str, Any] = self._client.get("/transcoder/jobs", params=params)
        return TranscoderJobList.from_dict(data)

    def get_job(self, uuid: str) -> TranscoderJob:
        data: dict[str, Any] = self._client.get(f"/transcoder/jobs/{uuid}")
        return TranscoderJob.from_dict(data)

    def get_job_outputs(self, uuid: str) -> TranscoderJobOutputs:
        """Files the job wrote to your bucket."""
        data: dict[str, Any] = self._client.get(f"/transcoder/jobs/{uuid}/outputs")
        return TranscoderJobOutputs.from_dict(data)

    def cancel_job(self, uuid: str) -> None:
        """Cancel a job that has not completed or failed. Files already written are kept."""
        self._client.delete(f"/transcoder/jobs/{uuid}")
