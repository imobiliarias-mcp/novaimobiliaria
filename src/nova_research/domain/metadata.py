"""Domain models for locations, cities, and neighborhoods."""

from dataclasses import dataclass, field


@dataclass(frozen=True)
class Neighborhood:
    """Individual neighborhood entity."""

    neighborhood_id: str
    name: str


@dataclass(frozen=True)
class City:
    """Individual municipality entity."""

    city_id: str
    name: str
    state_acronym: str


@dataclass(frozen=True)
class State:
    """Federative state containing municipalities."""

    state_id: str
    name: str
    acronym: str
    cities: list[City] = field(default_factory=list)


@dataclass(frozen=True)
class LocationCatalog:
    """First-class collection representing the portal's geographic coverage."""

    states: list[State] = field(default_factory=list)
    neighborhoods: list[Neighborhood] = field(default_factory=list)

    def find_city(self, city_id: str) -> City | None:
        """Find municipality by ID across all states."""
        for state in self.states:
            for city in state.cities:
                if city.city_id == city_id:
                    return city
        return None

    def find_neighborhood(self, neighborhood_id: str) -> Neighborhood | None:
        """Find neighborhood by ID."""
        for neighborhood in self.neighborhoods:
            if neighborhood.neighborhood_id == neighborhood_id:
                return neighborhood
        return None
