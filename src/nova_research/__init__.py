"""Nova Imobiliária rental research MCP package."""

from nova_research.client import NovaRentalClient
from nova_research.collaborators import RentalNetworkGateway, RentalParserSuite
from nova_research.domain.criteria import SearchCriteria
from nova_research.domain.enums import (
    AreaType,
    PropertyType,
    SortOrder,
    TransactionType,
)
from nova_research.domain.listing import (
    ListingCollection,
    ListingIdentity,
    ListingPricing,
    ListingSummary,
    PaginationMeta,
)
from nova_research.domain.metadata import City, LocationCatalog, Neighborhood, State
from nova_research.domain.property import Photo, PhotoGallery, PropertyDetail, PropertyLocation
from nova_research.domain.values import AreaRange, PageLimit, PageNumber, PriceRange, RoomCount
from nova_research.infrastructure.http_client import (
    HttpClientProtocol,
    HttpResponse,
    HttpxHttpClient,
    NetworkGatewayError,
    PropertyNotFoundError,
    SearchQueryError,
)
from nova_research.infrastructure.url_builder import UrlBuilder

__all__ = [
    "AreaRange",
    "AreaType",
    "City",
    "HttpClientProtocol",
    "HttpResponse",
    "HttpxHttpClient",
    "ListingCollection",
    "ListingIdentity",
    "ListingPricing",
    "ListingSummary",
    "LocationCatalog",
    "Neighborhood",
    "NetworkGatewayError",
    "NovaRentalClient",
    "PageLimit",
    "PageNumber",
    "PaginationMeta",
    "Photo",
    "PhotoGallery",
    "PriceRange",
    "PropertyDetail",
    "PropertyLocation",
    "PropertyNotFoundError",
    "PropertyType",
    "RentalNetworkGateway",
    "RentalParserSuite",
    "RoomCount",
    "SearchCriteria",
    "SearchQueryError",
    "SortOrder",
    "State",
    "TransactionType",
    "UrlBuilder",
]
