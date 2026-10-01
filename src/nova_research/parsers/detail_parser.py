"""Parser for transforming property detail JSON response into domain model."""

from typing import Any
from nova_research.domain.listing import ListingIdentity, ListingPricing
from nova_research.domain.property import Photo, PhotoGallery, PropertyDetail, PropertyLocation


class PropertyDetailParser:
    """Parses JSON response from Tecimob single property detail endpoint."""

    def parse(self, payload: dict[str, Any]) -> PropertyDetail:
        """Parse raw API dictionary payload into domain PropertyDetail."""
        data = payload.get("data", payload)
        identity = self._parse_identity(data)
        pricing = self._parse_pricing(data)
        return self._assemble_detail(data, identity, pricing)

    def _parse_identity(self, data: dict[str, Any]) -> ListingIdentity:
        """Extract identity from detail dictionary."""
        return ListingIdentity(
            property_id=str(data.get("id", "")),
            reference=str(data.get("reference", "")),
        )

    def _parse_pricing(self, data: dict[str, Any]) -> ListingPricing:
        """Extract pricing from detail dictionary."""
        return ListingPricing(
            amount=str(data.get("price", "Sob Consulta")),
            total_price=data.get("total_price"),
        )

    def _assemble_detail(
        self, data: dict[str, Any], identity: ListingIdentity, pricing: ListingPricing
    ) -> PropertyDetail:
        """Assemble full PropertyDetail entity."""
        title = str(data.get("title_formatted") or data.get("title") or "Imóvel")
        rooms = data.get("rooms", {}) if isinstance(data.get("rooms"), dict) else {}
        areas = data.get("areas", {}) if isinstance(data.get("areas"), dict) else {}
        return PropertyDetail(
            identity=identity, title=title, description=str(data.get("description", "")),
            pricing=pricing, location=self._parse_location(data), rooms_details=rooms,
            areas_details=areas, gallery=self._parse_gallery(data),
            canonical_path=str(data.get("url", "")), status=str(data.get("status", "")),
            situation=str(data.get("situation", "")),
        )

    def _parse_location(self, data: dict[str, Any]) -> PropertyLocation:
        """Extract property location structure."""
        addr = data.get("address", {})
        formatted = addr.get("formatted", "") if isinstance(addr, dict) else ""
        return PropertyLocation(formatted=str(formatted))

    def _parse_gallery(self, data: dict[str, Any]) -> PhotoGallery:
        """Extract photo gallery collection."""
        raw_images = data.get("images_extra", [])
        if not isinstance(raw_images, list):
            return PhotoGallery()
        photos = [self._to_photo(img) for img in raw_images if isinstance(img, dict)]
        return PhotoGallery(photos=photos)

    def _to_photo(self, img_dict: dict[str, Any]) -> Photo:
        """Map raw image dictionary to Photo domain model."""
        urls = img_dict.get("file_url", {})
        large = urls.get("large", "") if isinstance(urls, dict) else ""
        medium = urls.get("medium", "") if isinstance(urls, dict) else ""
        return Photo(
            photo_id=str(img_dict.get("id", "")),
            large_url=str(large),
            medium_url=str(medium),
        )
