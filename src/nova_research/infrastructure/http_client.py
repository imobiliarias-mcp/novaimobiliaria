"""HTTP client abstractions and implementations for Tecimob API communication."""

from dataclasses import dataclass
from typing import Any, Protocol
import httpx


class NetworkGatewayError(Exception):
    """Base exception for network communication failures."""


class PropertyNotFoundError(NetworkGatewayError):
    """Exception raised when a requested property cannot be found."""


class SearchQueryError(NetworkGatewayError):
    """Exception raised when search query execution fails."""


@dataclass(frozen=True)
class HttpResponse:
    """Encapsulates HTTP response data."""

    status_code: int
    text: str
    json_data: Any
    final_url: str


class HttpClientProtocol(Protocol):
    """Protocol defining network transport contract."""

    def get(self, url: str, params: dict[str, str] | None = None) -> HttpResponse:
        """Execute HTTP GET request."""
        ...


class HttpxHttpClient:
    """Concrete HTTP client utilizing httpx with Tecimob headers."""

    DEFAULT_DOMAIN = "jnovaimobiliaria.com.br"
    DEFAULT_TIMEOUT = 15.0

    def __init__(self, tenant_domain: str = DEFAULT_DOMAIN, timeout: float = DEFAULT_TIMEOUT) -> None:
        """Initialize HTTP client with tenant domain and timeout."""
        self._tenant_domain = tenant_domain
        self._timeout = timeout

    def get(self, url: str, params: dict[str, str] | None = None) -> HttpResponse:
        """Execute GET request with tenant header."""
        headers = self._build_headers()
        try:
            with httpx.Client(timeout=self._timeout) as client:
                resp = client.get(url, params=params, headers=headers)
                self._handle_response_status(resp, url)
                return self._to_http_response(resp)
        except httpx.HTTPError as exc:
            raise NetworkGatewayError(f"HTTP request to '{url}' failed: {exc}") from exc

    def _build_headers(self) -> dict[str, str]:
        """Construct required headers including multi-tenant x-domain."""
        return {
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36",
            "Accept": "application/json",
            "Content-Type": "application/json",
            "x-domain": self._tenant_domain,
        }

    def _handle_response_status(self, resp: httpx.Response, url: str) -> None:
        """Verify response status code."""
        if resp.status_code == 404:
            raise PropertyNotFoundError(f"Resource at '{url}' was not found (404).")
        if resp.status_code >= 400:
            raise SearchQueryError(f"Request failed with HTTP {resp.status_code}: {resp.text}")

    def _to_http_response(self, resp: httpx.Response) -> HttpResponse:
        """Convert httpx Response to HttpResponse."""
        json_data = resp.json() if resp.headers.get("content-type", "").startswith("application/json") else None
        return HttpResponse(
            status_code=resp.status_code,
            text=resp.text,
            json_data=json_data,
            final_url=str(resp.url),
        )
