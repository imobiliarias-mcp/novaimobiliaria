"""Domain value objects representing search parameters and constraints."""

from dataclasses import dataclass
from nova_research.domain.enums import AreaType


@dataclass(frozen=True)
class PriceRange:
    """Encapsulates minimum and maximum price constraints in Brazilian Reais."""

    minimum: int | None = None
    maximum: int | None = None

    def __post_init__(self) -> None:
        """Validate price constraints."""
        if self.minimum is not None and self.minimum < 0:
            raise ValueError("Minimum price cannot be negative")
        if self.maximum is not None and self.maximum < 0:
            raise ValueError("Maximum price cannot be negative")
        if self.minimum is not None and self.maximum is not None:
            if self.minimum > self.maximum:
                raise ValueError("Minimum price cannot exceed maximum price")

    def query_parameters(self) -> dict[str, str]:
        """Convert price range to Tecimob API filter query parameters."""
        params: dict[str, str] = {}
        if self.minimum is not None:
            params["filter[by_higher_than_price]"] = str(self.minimum)
        if self.maximum is not None:
            params["filter[by_lower_than_price]"] = str(self.maximum)
        return params


@dataclass(frozen=True)
class AreaRange:
    """Encapsulates area constraints with measurement unit."""

    minimum: int | None = None
    maximum: int | None = None
    area_type: AreaType = AreaType.TOTAL_AREA
    measure: str = "m²"

    def __post_init__(self) -> None:
        """Validate area constraints."""
        if self.minimum is not None and self.minimum < 0:
            raise ValueError("Minimum area cannot be negative")
        if self.maximum is not None and self.maximum < 0:
            raise ValueError("Maximum area cannot be negative")
        if self.minimum is not None and self.maximum is not None:
            if self.minimum > self.maximum:
                raise ValueError("Minimum area cannot exceed maximum area")

    def query_parameters(self) -> dict[str, str]:
        """Convert area range to Tecimob API filter query parameters."""
        params: dict[str, str] = {
            "filter[by_area][name]": self.area_type.value,
            "filter[by_area][measure]": self.measure,
        }
        if self.minimum is not None:
            params["filter[by_area][greater_equals]"] = str(self.minimum)
        if self.maximum is not None:
            params["filter[by_area][lower_equals]"] = str(self.maximum)
        return params


@dataclass(frozen=True)
class RoomCount:
    """Represents a room quantity constraint (exact or minimum)."""

    count: int
    is_minimum: bool = False

    def __post_init__(self) -> None:
        """Enforce non-negative room count."""
        if self.count < 0:
            raise ValueError("Room count cannot be negative")

    def query_parameter(self, room_field: str) -> tuple[str, str]:
        """Return parameter key and string value for the room specification."""
        comparison_key = "by_room_greater_equals" if self.is_minimum else "by_room_equals"
        return f"filter[{comparison_key}][{room_field}]", str(self.count)


@dataclass(frozen=True)
class PageNumber:
    """Represents a 1-indexed pagination number."""

    value: int = 1

    def __post_init__(self) -> None:
        """Enforce positive page index."""
        if self.value < 1:
            raise ValueError("Page index must be greater than or equal to 1")

    def to_param(self) -> str:
        """Return the string representation for query string."""
        return str(self.value)


@dataclass(frozen=True)
class PageLimit:
    """Represents the maximum number of items per page."""

    value: int = 21

    def __post_init__(self) -> None:
        """Enforce positive page limit."""
        if self.value < 1:
            raise ValueError("Page limit must be greater than or equal to 1")

    def to_param(self) -> str:
        """Return the string representation for query string."""
        return str(self.value)
