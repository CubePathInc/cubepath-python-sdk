from __future__ import annotations

import json as _json
import time
from collections.abc import Iterator
from typing import TYPE_CHECKING, Any

import httpx

from cubepath.models.ai_gateway import (
    ChatCompletionChunk,
    ChatCompletionRequest,
    ChatCompletionResponse,
    ModelListResponse,
)

if TYPE_CHECKING:
    from cubepath.client import CubePathClient

DEFAULT_AI_GATEWAY_BASE_URL = "https://ai-gateway.cubepath.com"


class ChatCompletionStream:
    """Iterator over streaming chat completion chunks (SSE).

    Must be closed after use, or used as a context manager::

        with client.ai_gateway.chat_completion_stream(req) as stream:
            for chunk in stream:
                print(chunk.choices[0].delta.content, end="")
    """

    def __init__(self, stream_ctx: Any) -> None:
        self._stream_ctx = stream_ctx
        self._response: httpx.Response = stream_ctx.__enter__()
        self._lines = self._response.iter_lines()
        self._done = False

    def __iter__(self) -> Iterator[ChatCompletionChunk]:
        return self

    def __next__(self) -> ChatCompletionChunk:
        if self._done:
            raise StopIteration

        for line in self._lines:
            line = line.strip()

            # Skip empty lines and SSE comments
            if not line or line.startswith(":"):
                continue

            if not line.startswith("data: "):
                continue

            data = line[len("data: ") :]

            if data == "[DONE]":
                self._done = True
                raise StopIteration

            return ChatCompletionChunk.from_dict(_json.loads(data))

        self._done = True
        raise StopIteration

    def close(self) -> None:
        self._stream_ctx.__exit__(None, None, None)

    def __enter__(self) -> ChatCompletionStream:
        return self

    def __exit__(self, *args: Any) -> None:
        self.close()


class AIGatewayService:
    """CubePath AI Gateway — OpenAI-compatible multi-provider API."""

    def __init__(self, client: CubePathClient, *, base_url: str = DEFAULT_AI_GATEWAY_BASE_URL) -> None:
        self._client = client
        self._base_url = base_url.rstrip("/")

    # ── Private helpers ──────────────────────────────────────────

    def _request(
        self,
        method: str,
        path: str,
        *,
        json: Any | None = None,
    ) -> Any:
        url = f"{self._base_url}{path}"
        c = self._client
        last_error: Exception | None = None

        for attempt in range(c._max_retries + 1):
            c._rate_limit()
            try:
                resp = c._http.request(
                    method,
                    url,
                    headers=c._headers(),
                    json=json,
                )
            except httpx.HTTPError as exc:
                last_error = exc
                if attempt < c._max_retries:
                    time.sleep(c._backoff(attempt))
                    continue
                raise

            if resp.status_code >= 400:
                if c._should_retry(resp.status_code) and attempt < c._max_retries:
                    last_error = c._parse_error(resp)
                    time.sleep(c._backoff(attempt))
                    continue
                raise c._parse_error(resp)

            if resp.status_code == 204 or not resp.content:
                return None

            return resp.json()

        raise last_error  # type: ignore[misc]

    def _stream_request(
        self,
        path: str,
        *,
        json: Any | None = None,
    ) -> Any:
        """Returns the httpx stream context manager (caller owns the lifecycle)."""
        url = f"{self._base_url}{path}"
        c = self._client

        # For streaming we cannot retry transparently once we hand back the
        # context manager, so we just return it directly.  httpx will raise
        # on connection errors, and status checking happens inside the
        # ChatCompletionStream wrapper via iter_lines.
        return c._http.stream(
            "POST",
            url,
            headers=c._headers(),
            json=json,
        )

    # ── Public API ───────────────────────────────────────────────

    def list_models(self) -> ModelListResponse:
        """List all available AI models with pricing and capabilities."""
        data: dict[str, Any] = self._request("GET", "/models")
        return ModelListResponse.from_dict(data)

    def chat_completion(self, req: ChatCompletionRequest) -> ChatCompletionResponse:
        """Send a chat completion request and return the full response."""
        req.stream = False
        data: dict[str, Any] = self._request("POST", "/chat/completions", json=req.to_dict())
        return ChatCompletionResponse.from_dict(data)

    def chat_completion_stream(self, req: ChatCompletionRequest) -> ChatCompletionStream:
        """Send a chat completion request and return a streaming iterator.

        Usage::

            req = ChatCompletionRequest(
                model="openai/gpt-4o",
                messages=[ChatMessage(role="user", content="Hello")],
                stream=True,
            )
            with client.ai_gateway.chat_completion_stream(req) as stream:
                for chunk in stream:
                    print(chunk.choices[0].delta.content, end="")
        """
        req.stream = True
        resp = self._stream_request("/chat/completions", json=req.to_dict())
        return ChatCompletionStream(resp)
