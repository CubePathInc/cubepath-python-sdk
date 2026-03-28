from __future__ import annotations


class APIError(Exception):
    """Error returned by the CubePath API."""

    def __init__(self, status_code: int, message: str, detail: str = "") -> None:
        self.status_code = status_code
        self.message = message
        self.detail = detail
        super().__init__(self.message)

    def __str__(self) -> str:
        if self.detail:
            return f"[{self.status_code}] {self.message}: {self.detail}"
        return f"[{self.status_code}] {self.message}"

    # Convenience checks matching the Go SDK
    def is_not_found(self) -> bool:
        return self.status_code == 404

    def is_conflict(self) -> bool:
        return self.status_code == 409

    def is_rate_limited(self) -> bool:
        return self.status_code == 429

    def is_bad_request(self) -> bool:
        return self.status_code == 400

    def is_server_error(self) -> bool:
        return self.status_code >= 500


# Module-level helpers
def is_not_found(err: BaseException) -> bool:
    return isinstance(err, APIError) and err.is_not_found()


def is_conflict(err: BaseException) -> bool:
    return isinstance(err, APIError) and err.is_conflict()


def is_rate_limited(err: BaseException) -> bool:
    return isinstance(err, APIError) and err.is_rate_limited()


def is_bad_request(err: BaseException) -> bool:
    return isinstance(err, APIError) and err.is_bad_request()
