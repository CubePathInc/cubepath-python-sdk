from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

__all__ = [
    "TranscoderS3Config",
    "TranscoderJobInput",
    "TranscoderJobOutput",
    "TranscoderOutputSpec",
    "CreateTranscoderJobRequest",
    "TranscoderBatchInput",
    "CreateTranscoderBatchRequest",
    "TranscoderJob",
    "TranscoderJobList",
    "TranscoderBatch",
    "TranscoderArtifact",
    "TranscoderJobOutputs",
]


@dataclass
class TranscoderS3Config:
    """A location in any S3 compatible bucket. The secret key is never returned by the API."""

    bucket: str
    path: str = ""
    """Object key (input) or destination prefix (output)."""
    endpoint: str | None = None
    """Omit for AWS."""
    region: str | None = None
    access_key: str | None = None
    secret_key: str | None = None

    def to_dict(self) -> dict[str, Any]:
        d: dict[str, Any] = {"bucket": self.bucket, "path": self.path}
        for k in ("endpoint", "region", "access_key", "secret_key"):
            v = getattr(self, k)
            if v is not None:
                d[k] = v
        return d

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> TranscoderS3Config:
        return cls(
            bucket=data.get("bucket", ""),
            path=data.get("path") or "",
            endpoint=data.get("endpoint"),
            region=data.get("region"),
            access_key=data.get("access_key"),
        )


@dataclass
class TranscoderJobInput:
    source: str
    """url or s3."""
    url: str | None = None
    s3: TranscoderS3Config | None = None

    def to_dict(self) -> dict[str, Any]:
        d: dict[str, Any] = {"source": self.source}
        if self.url is not None:
            d["url"] = self.url
        if self.s3 is not None:
            d["s3"] = self.s3.to_dict()
        return d

    @classmethod
    def from_dict(cls, data: dict[str, Any] | None) -> TranscoderJobInput:
        data = data or {}
        return cls(
            source=data.get("source", ""),
            url=data.get("url"),
            s3=TranscoderS3Config.from_dict(data["s3"]) if data.get("s3") else None,
        )


@dataclass
class TranscoderJobOutput:
    s3: TranscoderS3Config

    def to_dict(self) -> dict[str, Any]:
        return {"s3": self.s3.to_dict()}

    @classmethod
    def from_dict(cls, data: dict[str, Any] | None) -> TranscoderJobOutput:
        return cls(s3=TranscoderS3Config.from_dict((data or {}).get("s3") or {}))


@dataclass
class TranscoderOutputSpec:
    """One output format: type is file, hls, thumbnails or gif; options are its parameters (codec, crf...)."""

    type: str
    options: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {**self.options, "type": self.type}


@dataclass
class CreateTranscoderJobRequest:
    input: TranscoderJobInput
    output: TranscoderJobOutput
    outputs: list[TranscoderOutputSpec]
    """1 to 20 formats."""
    webhook_url: str | None = None
    """Called when the job completes or fails."""
    idempotency_key: str | None = None
    """Sending the same key again returns the original job instead of creating a new one."""

    def to_dict(self) -> dict[str, Any]:
        d: dict[str, Any] = {
            "input": self.input.to_dict(),
            "output": self.output.to_dict(),
            "outputs": [o.to_dict() for o in self.outputs],
        }
        if self.webhook_url is not None:
            d["webhook_url"] = self.webhook_url
        if self.idempotency_key is not None:
            d["idempotency_key"] = self.idempotency_key
        return d


@dataclass
class TranscoderBatchInput:
    """One input of a batch: a full s3 location, a url, or a path inside input_defaults.s3."""

    s3: TranscoderS3Config | None = None
    url: str | None = None
    path: str | None = None
    out_subpath: str | None = None
    """Appended as is to the output path: include your own separators."""

    def to_dict(self) -> dict[str, Any]:
        d: dict[str, Any] = {}
        if self.s3 is not None:
            d["s3"] = self.s3.to_dict()
        for k in ("url", "path", "out_subpath"):
            v = getattr(self, k)
            if v is not None:
                d[k] = v
        return d


@dataclass
class CreateTranscoderBatchRequest:
    output: TranscoderJobOutput
    outputs: list[TranscoderOutputSpec]
    inputs: list[TranscoderBatchInput]
    """1 to 1000 inputs; each becomes a job with the same outputs."""
    input_defaults: TranscoderJobInput | None = None
    webhook_url: str | None = None

    def to_dict(self) -> dict[str, Any]:
        d: dict[str, Any] = {
            "output": self.output.to_dict(),
            "outputs": [o.to_dict() for o in self.outputs],
            "inputs": [i.to_dict() for i in self.inputs],
        }
        if self.input_defaults is not None:
            d["input_defaults"] = self.input_defaults.to_dict()
        if self.webhook_url is not None:
            d["webhook_url"] = self.webhook_url
        return d


@dataclass
class TranscoderJob:
    uuid: str = ""
    status: str = ""
    """queued, analyzing, encoding, finalizing, completed, failed or canceled."""
    input: TranscoderJobInput | None = None
    output: TranscoderJobOutput | None = None
    spec: dict[str, Any] = field(default_factory=dict)
    outputs: list[dict[str, Any]] | None = None
    progress: int = 0
    total_segments: int = 0
    completed_segments: int = 0
    batch_id: str | None = None
    error: str | None = None
    created_at: str = ""

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> TranscoderJob:
        return cls(
            uuid=data.get("uuid", ""),
            status=data.get("status", ""),
            input=TranscoderJobInput.from_dict(data["input"]) if data.get("input") else None,
            output=TranscoderJobOutput.from_dict(data["output"]) if data.get("output") else None,
            spec=data.get("spec") or {},
            outputs=data.get("outputs"),
            progress=data.get("progress", 0),
            total_segments=data.get("total_segments", 0),
            completed_segments=data.get("completed_segments", 0),
            batch_id=data.get("batch_id"),
            error=data.get("error"),
            created_at=data.get("created_at", ""),
        )


@dataclass
class TranscoderJobList:
    jobs: list[TranscoderJob] = field(default_factory=list)
    limit: int = 0
    offset: int = 0

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> TranscoderJobList:
        return cls(
            jobs=[TranscoderJob.from_dict(j) for j in data.get("jobs", [])],
            limit=data.get("limit", 0),
            offset=data.get("offset", 0),
        )


@dataclass
class TranscoderBatch:
    batch_id: str = ""
    job_ids: list[str] = field(default_factory=list)
    count: int = 0

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> TranscoderBatch:
        return cls(batch_id=data.get("batch_id", ""), job_ids=data.get("job_ids", []), count=data.get("count", 0))


@dataclass
class TranscoderArtifact:
    type: str = ""
    bucket: str = ""
    key: str = ""

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> TranscoderArtifact:
        return cls(type=data.get("type", ""), bucket=data.get("bucket", ""), key=data.get("key", ""))


@dataclass
class TranscoderJobOutputs:
    outputs: list[TranscoderArtifact] = field(default_factory=list)
    """Empty until the job has finished."""
    destination: TranscoderJobOutput | None = None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> TranscoderJobOutputs:
        return cls(
            outputs=[TranscoderArtifact.from_dict(o) for o in data.get("outputs") or []],
            destination=TranscoderJobOutput.from_dict(data["destination"]) if data.get("destination") else None,
        )
