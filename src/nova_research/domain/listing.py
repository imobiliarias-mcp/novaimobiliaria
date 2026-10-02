"""Domain models for listing cards and paginated collections."""

from collections.abc import Iterator
from dataclasses import asdict, dataclass, field
from typing import Any
from urllib.parse import SplitResult, urlsplit

API_HOST = "api-sites.tecimob.com.br"
IMAGE_FILE_SUFFIXES = (".jpg", ".jpeg", ".png", ".webp", ".gif", ".svg", ".avif")
SEARCH_ROUTE_PREFIXES = ("/alugar/imoveis/",)


def is_valid_public_listing_url(url: str) -> bool:
    """Validate public listing pages, excluding known API, image, and search URLs."""
    try:
        parsed_url = urlsplit(url)
        hostname = parsed_url.hostname
        port = parsed_url.port
    except ValueError:
        return False
    return _has_valid_public_authority(parsed_url, hostname, port) and _is_property_path(
        parsed_url.path
    )


def _has_valid_public_authority(
    parsed_url: SplitResult, hostname: str | None, port: int | None
) -> bool:
    return (
        parsed_url.scheme.lower() in {"http", "https"}
        and bool(hostname)
        and hostname.lower() != API_HOST
        and parsed_url.username is None
        and parsed_url.password is None
        and not any(character.isspace() for character in parsed_url.netloc)
        and not parsed_url.netloc.endswith(":")
        and (port is None or 0 <= port <= 65535)
    )


def _is_property_path(path: str) -> bool:
    normalized_path = path.lower()
    if normalized_path.endswith(IMAGE_FILE_SUFFIXES):
        return False
    return not normalized_path.startswith(SEARCH_ROUTE_PREFIXES)


class InvalidListingUrlError(ValueError):
    """Raised when a listing lacks a valid public property URL."""


@dataclass(frozen=True)
class ListingIdentity:
    """Unique identity and reference identifiers for a listing."""

    property_id: str
    reference: str


@dataclass(frozen=True)
class ListingPricing:
    """Pricing information for a listing."""

    amount: str
    total_price: str | None = None


@dataclass(frozen=True)
class PaginationMeta:
    """Metadata regarding pagination state."""

    total: int
    per_page: int
    current_page: int
    total_pages: int

    @property
    def has_next_page(self) -> bool:
        """Indicate whether subsequent pages exist."""
        return self.current_page < self.total_pages


@dataclass(frozen=True)
class ListingSummary:
    """Summary of a property listing card returned by search queries."""

    identity: ListingIdentity
    title: str
    pricing: ListingPricing
    address_formatted: str
    rooms_summary: str
    primary_area: str | None
    thumbnail_url: str | None
    canonical_path: str
    url: str = ""

    def to_dictionary(self) -> dict[str, Any]:
        """Serialize all summary fields after validating the public URL."""
        self._validate_public_url()
        return asdict(self)

    def _validate_public_url(self) -> None:
        """Reject invalid or non-property URLs with listing identity context."""
        if is_valid_public_listing_url(self.url):
            return
        raise InvalidListingUrlError(
            f"Listing {self.identity.property_id} has invalid public URL {self.url!r}."
        )


@dataclass(frozen=True)
class ListingCollection:
    """First-class collection wrapping a sequence of ListingSummary objects."""

    items: list[ListingSummary] = field(default_factory=list)
    meta: PaginationMeta | None = None

    def __len__(self) -> int:
        """Return the number of listings in this page."""
        return len(self.items)

    def __iter__(self) -> Iterator[ListingSummary]:
        """Iterate over listings."""
        return iter(self.items)

    def __getitem__(self, index: int) -> ListingSummary:
        """Access listing by integer index."""
        return self.items[index]

    def first(self) -> ListingSummary | None:
        """Return the first listing or None if empty."""
        return self.items[0] if self.items else None

    def to_dictionary(self) -> dict[str, Any]:
        """Serialize typed listings and preserve pagination metadata."""
        pagination = asdict(self.meta) if self.meta else None
        return {
            "items": [listing.to_dictionary() for listing in self.items],
            "meta": pagination,
            "returned_count": len(self.items),
        }
