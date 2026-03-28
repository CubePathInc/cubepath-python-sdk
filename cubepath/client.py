from __future__ import annotations

import random
import time
from typing import Any

import httpx

from cubepath.exceptions import APIError

DEFAULT_BASE_URL = "https://api.cubepath.com"
SDK_VERSION = "0.1.0"
DEFAULT_TIMEOUT = 30.0
DEFAULT_MAX_RETRIES = 3
DEFAULT_RETRY_WAIT_MIN = 1.0
DEFAULT_RETRY_WAIT_MAX = 30.0
DEFAULT_RATE_LIMIT_INTERVAL = 0.1  # 10 req/s


class CubePathClient:
    """CubePath API client — Python equivalent of the Go SDK."""

    def __init__(
        self,
        api_token: str,
        *,
        base_url: str = DEFAULT_BASE_URL,
        timeout: float = DEFAULT_TIMEOUT,
        max_retries: int = DEFAULT_MAX_RETRIES,
        retry_wait_min: float = DEFAULT_RETRY_WAIT_MIN,
        retry_wait_max: float = DEFAULT_RETRY_WAIT_MAX,
        rate_limit_interval: float = DEFAULT_RATE_LIMIT_INTERVAL,
        http_client: httpx.Client | None = None,
        user_agent: str | None = None,
    ) -> None:
        self._api_token = api_token
        self._base_url = base_url.rstrip("/")
        self._max_retries = max_retries
        self._retry_wait_min = retry_wait_min
        self._retry_wait_max = retry_wait_max
        self._rate_limit_interval = rate_limit_interval
        self._last_request_time: float = 0.0
        self._user_agent = user_agent or f"cubepath-sdk-python/{SDK_VERSION}"

        if http_client is not None:
            self._http = http_client
        else:
            transport = httpx.HTTPTransport(
                retries=0,  # we handle retries ourselves
            )
            self._http = httpx.Client(
                timeout=timeout,
                transport=transport,
            )

        # Lazy-init services
        from cubepath.services.baremetal import BaremetalService
        from cubepath.services.cdn import CDNService
        from cubepath.services.ddos import DDoSService
        from cubepath.services.dns import DNSService
        from cubepath.services.firewall import FirewallService
        from cubepath.services.floating_ips import FloatingIPService
        from cubepath.services.kubernetes import KubernetesService
        from cubepath.services.load_balancer import LoadBalancerService
        from cubepath.services.networks import NetworkService
        from cubepath.services.pricing import PricingService
        from cubepath.services.projects import ProjectService
        from cubepath.services.ssh_keys import SSHKeyService
        from cubepath.services.vps import VPSService

        self.projects = ProjectService(self)
        self.ssh_keys = SSHKeyService(self)
        self.vps = VPSService(self)
        self.baremetal = BaremetalService(self)
        self.networks = NetworkService(self)
        self.floating_ips = FloatingIPService(self)
        self.firewall = FirewallService(self)
        self.dns = DNSService(self)
        self.load_balancer = LoadBalancerService(self)
        self.cdn = CDNService(self)
        self.kubernetes = KubernetesService(self)
        self.pricing = PricingService(self)
        self.ddos = DDoSService(self)

    # ── HTTP helpers ──────────────────────────────────────────────

    def _headers(self) -> dict[str, str]:
        return {
            "Authorization": f"Bearer {self._api_token}",
            "Content-Type": "application/json",
            "Accept": "application/json",
            "User-Agent": self._user_agent,
        }

    def _rate_limit(self) -> None:
        now = time.monotonic()
        elapsed = now - self._last_request_time
        if elapsed < self._rate_limit_interval:
            time.sleep(self._rate_limit_interval - elapsed)
        self._last_request_time = time.monotonic()

    def _backoff(self, attempt: int) -> float:
        wait = self._retry_wait_min * (2 ** attempt)
        wait = min(wait, self._retry_wait_max)
        jitter = random.uniform(0, wait * 0.5)  # noqa: S311
        return wait + jitter

    @staticmethod
    def _parse_error(response: httpx.Response) -> APIError:
        try:
            body = response.json()
            # FastAPI-style {"detail": "..."} or {"message": "...", "detail": "..."}
            if isinstance(body, dict):
                detail = body.get("detail", "")
                message = body.get("message", str(detail) if detail else response.reason_phrase)
                if isinstance(detail, list):
                    detail = str(detail)
                return APIError(response.status_code, str(message), str(detail))
        except Exception:
            pass
        return APIError(response.status_code, response.reason_phrase, response.text)

    def _should_retry(self, status_code: int) -> bool:
        return status_code == 429 or status_code >= 500

    def request(
        self,
        method: str,
        path: str,
        *,
        json: Any | None = None,
        params: dict[str, Any] | None = None,
        raw: bool = False,
    ) -> Any:
        """Execute an API request with rate-limiting and retries.

        Returns parsed JSON (dict/list) or raw bytes when *raw=True*.
        """
        url = f"{self._base_url}{path}"
        last_error: Exception | None = None

        for attempt in range(self._max_retries + 1):
            self._rate_limit()
            try:
                resp = self._http.request(
                    method,
                    url,
                    headers=self._headers(),
                    json=json,
                    params=params,
                )
            except httpx.HTTPError as exc:
                last_error = exc
                if attempt < self._max_retries:
                    time.sleep(self._backoff(attempt))
                    continue
                raise

            if resp.status_code >= 400:
                if self._should_retry(resp.status_code) and attempt < self._max_retries:
                    last_error = self._parse_error(resp)
                    time.sleep(self._backoff(attempt))
                    continue
                raise self._parse_error(resp)

            if raw:
                return resp.content

            if resp.status_code == 204 or not resp.content:
                return None

            return resp.json()

        raise last_error  # type: ignore[misc]

    # Convenience wrappers
    def get(self, path: str, *, params: dict[str, Any] | None = None) -> Any:
        return self.request("GET", path, params=params)

    def post(self, path: str, *, json: Any | None = None, params: dict[str, Any] | None = None) -> Any:
        return self.request("POST", path, json=json, params=params)

    def put(self, path: str, *, json: Any | None = None) -> Any:
        return self.request("PUT", path, json=json)

    def patch(self, path: str, *, json: Any | None = None) -> Any:
        return self.request("PATCH", path, json=json)

    def delete(self, path: str, *, params: dict[str, Any] | None = None) -> Any:
        return self.request("DELETE", path, params=params)

    def get_raw(self, path: str, *, params: dict[str, Any] | None = None) -> bytes:
        return self.request("GET", path, params=params, raw=True)  # type: ignore[return-value]

    def close(self) -> None:
        self._http.close()

    def __enter__(self) -> CubePathClient:
        return self

    def __exit__(self, *args: Any) -> None:
        self.close()
