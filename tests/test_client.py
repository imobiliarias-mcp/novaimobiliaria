"""Unit tests for NovaRentalClient with mock HTTP transport."""

import pytest
from nova_research.client import NovaRentalClient
from nova_research.collaborators import RentalNetworkGateway, RentalParserSuite
from nova_research.domain.criteria import SearchCriteria
from nova_research.infrastructure.http_client import (
    HttpClientProtocol,
    HttpResponse,
    PropertyNotFoundError,
    SearchQueryError,
)
from nova_research.infrastructure.url_builder import UrlBuilder


class StubHttpClient(HttpClientProtocol):
    """Stub HTTP client returning predefined responses."""

    def __init__(self, responses: dict[str, HttpResponse]) -> None:
        """Initialize with response map keyed by URL substring."""
        self._responses = responses

    def get(self, url: str, params: dict[str, str] | None = None) -> HttpResponse:
        """Return matching stub response or 404."""
        for key, resp in self._responses.items():
            if key in url:
                if resp.status_code == 404:
                    raise PropertyNotFoundError(f"Not found: {url}")
                if resp.status_code >= 400:
                    raise SearchQueryError(f"Error: {resp.status_code}")
                return resp
        return HttpResponse(200, "{}", {}, url)


def test_client_search_with_stub() -> None:
    """Test client search method with stub response."""
    stub_payload = {
        "meta": {"pagination": {"total": 1, "per_page": 21, "current_page": 1, "total_pages": 1}},
        "data": [{"id": "1", "reference": "100", "title_formatted": "Casa", "price": "R$1.000,00"}],
    }
    client_stub = StubHttpClient({"properties": HttpResponse(200, "", stub_payload, "http://api/properties")})
    gateway = RentalNetworkGateway(http_client=client_stub)
    client = NovaRentalClient(gateway=gateway)

    result = client.search(SearchCriteria())
    assert len(result) == 1
    assert result[0].identity.reference == "100"


def test_client_search_rentals_convenience() -> None:
    """Test client search_rentals helper."""
    stub_payload = {
        "meta": {"pagination": {"total": 1, "per_page": 21, "current_page": 1, "total_pages": 1}},
        "data": [{"id": "2", "reference": "200", "title_formatted": "Apto", "price": "R$2.000,00"}],
    }
    client_stub = StubHttpClient({"properties": HttpResponse(200, "", stub_payload, "http://api/properties")})
    gateway = RentalNetworkGateway(http_client=client_stub)
    client = NovaRentalClient(gateway=gateway)

    result = client.search_rentals(city="timoteo-mg", bedrooms=2, max_price=2500)
    assert len(result) == 1
    assert result[0].identity.reference == "200"


def test_client_get_details_not_found() -> None:
    """Test client get_details handling 404 error."""
    client_stub = StubHttpClient({"properties/999": HttpResponse(404, "Not Found", None, "http://api/properties/999")})
    gateway = RentalNetworkGateway(http_client=client_stub)
    client = NovaRentalClient(gateway=gateway)

    with pytest.raises(PropertyNotFoundError):
        client.get_details("999")
