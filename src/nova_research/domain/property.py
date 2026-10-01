"""Domain models for full property details and photo galleries."""

from collections.abc import Iterator
from dataclasses import dataclass, field
from typing import Any
from nova_research.domain.listing import ListingIdentity, ListingPricing


@dataclass(frozen=True)
class Photo:
    """Individual photograph with multiple resolution variants."""

    photo_id: str
    large_url: str
    medium_url: str


@dataclass(frozen=True)
class PhotoGallery:
    """First-class collection representing a property's photo gallery."""

    photos: list[Photo] = field(default_factory=list)

    def __len__(self) -> int:
        """Return the number of photos in the gallery."""
        return len(self.photos)

    def __iter__(self) -> Iterator[Photo]:
        """Iterate over photos in the gallery."""
        return iter(self.photos)

    def __getitem__(self, index: int) -> Photo:
        """Access photo by integer index."""
        return self.photos[index]

    def first_photo(self) -> Photo | None:
        """Return the primary photo or None if empty."""
        return self.photos[0] if self.photos else None

    def large_urls(self) -> list[str]:
        """Return all large-resolution photo URLs."""
        return [photo.large_url for photo in self.photos]


@dataclass(frozen=True)
class PropertyLocation:
    """Geographic and formatted address information."""

    formatted: str


@dataclass(frozen=True)
class PropertyDetail:
    """Complete detail representation of a property."""

    identity: ListingIdentity
    title: str
    description: str
    pricing: ListingPricing
    location: PropertyLocation
    rooms_details: dict[str, Any]
    areas_details: dict[str, Any]
    gallery: PhotoGallery
    canonical_path: str
    status: str
    situation: str
