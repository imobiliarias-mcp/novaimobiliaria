"""Parser for transforming search JSON responses into domain collections."""

from typing import Any
from nova_research.domain.listing import (
    ListingCollection,
    ListingIdentity,
    ListingPricing,
    ListingSummary,
    PaginationMeta,
)


class SearchPageParser:
    """Parses JSON responses from Tecimob property search endpoint."""

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
        title = str(item.get("title_formatted") or item.get("title") or "Imóvel")
        return ListingSummary(
            identity=self._extract_identity(item),
            title=title,
            pricing=self._extract_pricing(item),
            address_formatted=self._extract_address(item),
            rooms_summary=self._extract_rooms_summary(item),
            primary_area=self._extract_primary_area(item),
            thumbnail_url=self._extract_thumbnail(item),
            canonical_path=str(item.get("url", "")),
        )

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
