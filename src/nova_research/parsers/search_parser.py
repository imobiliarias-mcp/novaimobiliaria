"""Parser for transforming search JSON responses into domain collections."""

from typing import Any
from urllib.parse import urljoin
from nova_research.domain.listing import (
    InvalidListingUrlError,
    is_valid_public_listing_url,
    ListingCollection,
    ListingIdentity,
    ListingPricing,
    ListingSummary,
    PaginationMeta,
)


PUBLIC_BASE_URL = "https://jnovaimobiliaria.com.br/"


class SearchPageParser:
    """Parses JSON responses from Tecimob property search endpoint."""

    def __init__(self, public_base_url: str = PUBLIC_BASE_URL) -> None:
        """Configure the distinct public-site origin for listing URLs."""
        self._public_base_url = self._validate_public_base_url(public_base_url)

    def parse(self, payload: dict[str, Any]) -> ListingCollection:
        """Parse raw API dictionary payload into domain ListingCollection."""
        meta = self._parse_pagination(payload.get("meta", {}))
        items_data = payload.get("data", [])
        listings = [self._parse_item(item) for item in items_data]
        return ListingCollection(items=listings, meta=meta)

    def _parse_pagination(self, meta_dict: dict[str, Any]) -> PaginationMeta | None:
        """Extract pagination metadata if available."""
        pag = meta_dict.get("pagination")
        if not pag or pag.get("total") is None:
            return None
        return PaginationMeta(
            total=int(pag.get("total", 0)),
            per_page=int(pag.get("per_page", 21)),
            current_page=int(pag.get("current_page", 1)),
            total_pages=int(pag.get("total_pages", 1)),
        )

    def _parse_item(self, item: dict[str, Any]) -> ListingSummary:
        """Map raw property card dictionary to domain ListingSummary."""
        identity = self._extract_identity(item)
        canonical_path = str(item.get("url") or "")
        public_url = self._resolve_public_url(canonical_path, identity.property_id)
        title = str(item.get("title_formatted") or item.get("title") or "Imóvel")
        return ListingSummary(
            identity=identity,
            title=title,
            pricing=self._extract_pricing(item),
            address_formatted=self._extract_address(item),
            rooms_summary=self._extract_rooms_summary(item),
            primary_area=self._extract_primary_area(item),
            thumbnail_url=self._extract_thumbnail(item),
            canonical_path=canonical_path,
            url=public_url,
        )

    def _resolve_public_url(self, canonical_path: str, property_id: str) -> str:
        """Resolve and validate a card URL without relying on its API origin."""
        if not canonical_path.strip():
            raise InvalidListingUrlError(
                f"Listing {property_id} has no recoverable public URL."
            )
        try:
            public_url = urljoin(self._public_base_url, canonical_path)
        except ValueError as error:
            raise InvalidListingUrlError(
                f"Listing {property_id} has invalid public URL {canonical_path!r}."
            ) from error
        if not is_valid_public_listing_url(public_url):
            raise InvalidListingUrlError(
                f"Listing {property_id} has invalid public URL {canonical_path!r}."
            )
        return public_url

    def _validate_public_base_url(self, public_base_url: str) -> str:
        """Reject an invalid public origin before parsing listings."""
        if not is_valid_public_listing_url(public_base_url):
            raise ValueError(f"Invalid public base URL: {public_base_url!r}.")
        return f"{public_base_url.rstrip('/')}/"

    def _extract_identity(self, item: dict[str, Any]) -> ListingIdentity:
        """Extract identity value object."""
        return ListingIdentity(
            property_id=str(item.get("id", "")), reference=str(item.get("reference", ""))
        )

    def _extract_pricing(self, item: dict[str, Any]) -> ListingPricing:
        """Extract pricing value object."""
        return ListingPricing(
            amount=str(item.get("price", "Sob Consulta")), total_price=item.get("total_price")
        )

    def _extract_address(self, item: dict[str, Any]) -> str:
        """Extract formatted address string."""
        addr = item.get("address", {})
        if isinstance(addr, dict):
            return str(addr.get("formatted", ""))
        return ""

    def _extract_rooms_summary(self, item: dict[str, Any]) -> str:
        """Extract concise room summary from rooms map."""
        rooms = item.get("rooms", {})
        if not isinstance(rooms, dict):
            return ""
        descriptions = [
            str(r.get("title_formated"))
            for r in rooms.values()
            if isinstance(r, dict) and r.get("title_formated")
        ]
        return ", ".join(descriptions)

    def _extract_primary_area(self, item: dict[str, Any]) -> str | None:
        """Extract primary area measure string."""
        areas = item.get("areas")
        if isinstance(areas, dict) and "primary_area" in areas:
            p = areas["primary_area"]
            return f"{p.get('value', '')} {p.get('measure', 'm²')}".strip()
        return None

    def _extract_thumbnail(self, item: dict[str, Any]) -> str | None:
        """Extract first image thumbnail URL."""
        images = item.get("images_extra", [])
        if images and isinstance(images, list) and isinstance(images[0], dict):
            urls = images[0].get("file_url", {})
            return urls.get("medium") or urls.get("large")
        return None
