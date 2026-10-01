"""Central rental research MCP interface and client."""

from nova_research.collaborators import RentalNetworkGateway, RentalParserSuite
from nova_research.domain.criteria import SearchCriteria
from nova_research.domain.enums import PropertyType
from nova_research.domain.listing import ListingCollection
from nova_research.domain.metadata import LocationCatalog
from nova_research.domain.property import PropertyDetail


class NovaRentalClient:
    """Central rental research client serving as the project's MCP interface."""

    def __init__(
        self,
        gateway: RentalNetworkGateway | None = None,
        parsers: RentalParserSuite | None = None,
    ) -> None:
        """Initialize client with network gateway and parser suite collaborators."""
        self._gateway = gateway or RentalNetworkGateway()
        self._parsers = parsers or RentalParserSuite()

    def search(self, criteria: SearchCriteria) -> ListingCollection:
        """Execute search query and return parsed collection of listings."""
        resp = self._gateway.fetch_search(criteria)
        parser = self._parsers.search_parser
        return parser.parse(resp.json_data or {})

    def search_rentals(
        self,
        city: str = "timoteo-mg",
        property_type: PropertyType = PropertyType.TODOS,
        bedrooms: int | None = None,
        max_price: int | None = None,
        page: int = 1,
    ) -> ListingCollection:
        """Execute rental search with standard filters."""
        criteria = SearchCriteria.create_rental(
            city=city, property_type=property_type, bedrooms=bedrooms, max_price=max_price, page=page
        )
        return self.search(criteria)

    def get_details(self, property_id_or_reference: str) -> PropertyDetail:
        """Retrieve full details for a specific property by ID or reference code."""
        resp = self._gateway.fetch_detail(property_id_or_reference)
        parser = self._parsers.detail_parser
        return parser.parse(resp.json_data or {})

    def get_locations(self) -> LocationCatalog:
        """Retrieve catalog of states, cities, and neighborhoods."""
        states_resp = self._gateway.fetch_states()
        neighs_resp = self._gateway.fetch_neighborhoods()
        parser = self._parsers.metadata_parser
        return parser.parse(
            states_payload=states_resp.json_data,
            neighborhoods_payload=neighs_resp.json_data,
        )
