"""Model Context Protocol (MCP) tool adapters for Central Rental Research."""

from typing import Any
from nova_research.client import NovaRentalClient


class NovaMcpAdapter:
    """Adapts Nova Imobiliária rental client for consumption by MCP servers and tool registries."""

    def __init__(self, client: Any = None) -> None:
        """Initialize adapter with an abstract rental client."""
        self._client = client or NovaRentalClient()

    @classmethod
    def create_default(cls) -> "NovaMcpAdapter":
        """Factory constructor instantiating the default Nova provider."""
        return cls()

    def search_rentals(
        self,
        city: str = "timoteo-mg",
        min_price: float = 0.0,
        max_price: float = 0.0,
        bedrooms: int = 0,
        property_type: str = "",
        page: int = 1,
    ) -> dict[str, Any]:
        """Execute a rental property search for an MCP tool call."""
        c = city.lower() if city else "timoteo-mg"
        b = bedrooms if bedrooms > 0 else None
        p = int(max_price) if max_price > 0 else None
        results = self._client.search_rentals(
            city=c,
            bedrooms=b,
            max_price=p,
            page=page,
        )
        return self._format_collection(results)

    def _format_collection(self, collection: Any) -> dict[str, Any]:
        """Format collection into standard dictionary."""
        return {
            "provider": "novaimobiliaria",
            "total_count": len(collection),
            "listings": [self._format_item(item) for item in collection],
        }

    def _format_item(self, item: Any) -> dict[str, Any]:
        """Format individual listing item."""
        loc = getattr(item, "location", None)
        specs = getattr(item, "specs", None)
        return {
            "id": _identity_value(item, "property_id"),
            "code": _identity_value(item, "reference") or _identity_value(item, "property_id"),
            "title": getattr(item, "title", ""),
            "price": getattr(item, "price_formatted", ""),
            "url": getattr(item, "url", ""),
            "media_url": getattr(item, "thumbnail_url", None) or "",
            "neighborhood": getattr(loc, "neighborhood", "") if loc else "",
            "city": getattr(loc, "city", "") if loc else "",
            "bedrooms": getattr(specs, "bedrooms", 0) if specs else 0,
            "bathrooms": getattr(specs, "bathrooms", 0) if specs else 0,
        }

    def get_property_detail(self, property_code: str) -> dict[str, Any]:
        """Retrieve complete property detail for an MCP tool call."""
        detail = self._client.get_details(property_code)
        loc = getattr(detail, "location", None)
        specs = getattr(detail, "specs", None)
        return {
            "id": _identity_value(detail, "property_id") or str(property_code),
            "code": _identity_value(detail, "reference") or _identity_value(detail, "property_id"),
            "title": getattr(detail, "title", ""),
            "description": getattr(detail, "description", ""),
            "price": getattr(detail, "price_formatted", ""),
            "url": getattr(detail, "url", ""),
            "neighborhood": getattr(loc, "neighborhood", "") if loc else "",
            "city": getattr(loc, "city", "") if loc else "",
            "bedrooms": getattr(specs, "bedrooms", 0) if specs else 0,
            "bathrooms": getattr(specs, "bathrooms", 0) if specs else 0,
            "parking_spaces": getattr(specs, "parking_spaces", 0) if specs else 0,
            "area": getattr(specs, "area", 0.0) if specs else 0.0,
            "photos": _gallery_urls(detail),
        }

    def get_facets(self) -> dict[str, Any]:
        """Retrieve available search facets for an MCP tool call."""
        locations = self._client.get_locations()
        cities = [{"name": getattr(c, "name", "")} for c in getattr(locations, "cities", [])]
        return {"cities": cities}

    def get_provider_info(self) -> dict[str, Any]:
        """Retrieve metadata about this rental provider adapter."""
        return {
            "provider_name": "novaimobiliaria",
            "coverage_region": "Timóteo, Coronel Fabriciano, Ipatinga",
            "supported_operations": ["search_rentals", "get_property_detail", "get_facets"],
        }


def _identity_value(entity: Any, name: str) -> str:
    """Read an identifier from the entity's identity block, falling back to a flat attribute."""
    identity = getattr(entity, "identity", None)
    source = identity if identity is not None else entity
    return str(getattr(source, name, "") or "")


def _gallery_urls(detail: Any) -> list[str]:
    """Return one URL per photo, preferring the large variant and skipping photos without any URL."""
    gallery = getattr(detail, "gallery", None)
    photos = getattr(gallery, "photos", []) if gallery is not None else []
    urls = (photo.large_url or photo.medium_url for photo in photos)
    return [url for url in urls if url]

