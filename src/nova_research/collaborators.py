"""Network gateway and parser suite collaborators for Nova rental client."""

from nova_research.domain.criteria import SearchCriteria
from nova_research.infrastructure.http_client import (
    HttpClientProtocol,
    HttpResponse,
    HttpxHttpClient,
)
from nova_research.infrastructure.url_builder import UrlBuilder
from nova_research.parsers.detail_parser import PropertyDetailParser
from nova_research.parsers.metadata_parser import MetadataParser
from nova_research.parsers.search_parser import SearchPageParser


class RentalNetworkGateway:
    """Dispatches HTTP requests for rental searches, details, and catalog filters."""

    def __init__(
        self,
        http_client: HttpClientProtocol | None = None,
        url_builder: UrlBuilder | None = None,
    ) -> None:
        """Initialize gateway with network client and URL builder."""
        self._http = http_client or HttpxHttpClient()
        self._builder = url_builder or UrlBuilder()

    def fetch_search(self, criteria: SearchCriteria) -> HttpResponse:
        """Fetch search listings matching criteria."""
        url = self._builder.build_search_url()
        params = criteria.to_query_parameters()
        return self._http.get(url, params=params)

    def fetch_detail(self, property_id_or_reference: str) -> HttpResponse:
        """Fetch detail payload for a property ID or reference code."""
        url = self._builder.build_detail_url(property_id_or_reference)
        return self._http.get(url)

    def fetch_states(self) -> HttpResponse:
        """Fetch states and cities filter catalog."""
        url = self._builder.build_states_filter_url()
        return self._http.get(url, params={"sort": "acronym"})

    def fetch_neighborhoods(self) -> HttpResponse:
        """Fetch neighborhoods filter catalog."""
        url = self._builder.build_neighborhoods_filter_url()
        return self._http.get(url, params={"sort": "slug"})


class RentalParserSuite:
    """Composite suite aggregating search, detail, and metadata parsers."""

    def __init__(
        self,
        search_parser: SearchPageParser | None = None,
        detail_parser: PropertyDetailParser | None = None,
    ) -> None:
        """Initialize parser suite with core parsers."""
        self._search = search_parser or SearchPageParser()
        self._detail = detail_parser or PropertyDetailParser()
        self._metadata = MetadataParser()

    @property
    def search_parser(self) -> SearchPageParser:
        """Return search parser collaborator."""
        return self._search

    @property
    def detail_parser(self) -> PropertyDetailParser:
        """Return detail parser collaborator."""
        return self._detail

    @property
    def metadata_parser(self) -> MetadataParser:
        """Return metadata parser collaborator."""
        return self._metadata
