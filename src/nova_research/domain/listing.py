"""Domain models for listing cards and paginated collections."""

from collections.abc import Iterator
from dataclasses import dataclass, field


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
