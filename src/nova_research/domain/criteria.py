"""Search criteria encapsulating rental query parameters."""

from dataclasses import dataclass
from nova_research.domain.enums import PropertyType, SortOrder, TransactionType
from nova_research.domain.values import AreaRange, PageLimit, PageNumber, PriceRange, RoomCount


@dataclass(frozen=True)
class SearchCriteria:
    """Encapsulates all search criteria for listing queries."""

    transaction: TransactionType = TransactionType.ALUGAR
    location_slug: str = "timoteo-mg"
    property_type: PropertyType = PropertyType.TODOS
    price: PriceRange = PriceRange()
    area: AreaRange | None = None
    bedrooms: RoomCount | None = None
    suites: RoomCount | None = None
    garages: RoomCount | None = None
    sort: SortOrder = SortOrder.RECENT
    page: PageNumber = PageNumber()
    limit: PageLimit = PageLimit()

    @classmethod
    def create_rental(
        cls, city: str = "timoteo-mg", property_type: PropertyType = PropertyType.TODOS,
        bedrooms: int | None = None, max_price: int | None = None, page: int = 1,
    ) -> "SearchCriteria":
        """Factory for building standard rental search criteria."""
        room = RoomCount(count=bedrooms) if bedrooms is not None else None
        price = PriceRange(maximum=max_price)
        return cls(
            location_slug=city, property_type=property_type, price=price,
            bedrooms=room, page=PageNumber(value=page),
        )

    def to_query_parameters(self) -> dict[str, str]:
        """Convert domain criteria to Tecimob API query parameters."""
        params: dict[str, str] = {
            "custom_query": "card",
            "sort": self.sort.value,
            "offset": self.page.to_param(),
            "limit": self.limit.to_param(),
            "filter[transaction]": self.transaction.value,
        }
        self._apply_location_and_type(params)
        self._apply_ranges(params)
        self._apply_rooms(params)
        return params

    def _apply_location_and_type(self, params: dict[str, str]) -> None:
        """Apply location and property type constraints."""
        if self.location_slug:
            params["filter[by_neighborhood_or_city_slug]"] = self.location_slug
        if self.property_type != PropertyType.TODOS:
            params["filter[by_type_or_subtype_slug]"] = self.property_type.value

    def _apply_ranges(self, params: dict[str, str]) -> None:
        """Apply price and area range filters."""
        params.update(self.price.query_parameters())
        if self.area is not None:
            params.update(self.area.query_parameters())

    def _apply_rooms(self, params: dict[str, str]) -> None:
        """Apply bedroom, suite, and garage filters."""
        if self.bedrooms is not None:
            k, v = self.bedrooms.query_parameter("bedroom")
            params[k] = v
        if self.suites is not None:
            k, v = self.suites.query_parameter("suite")
            params[k] = v
        if self.garages is not None:
            k, v = self.garages.query_parameter("garage")
            params[k] = v
