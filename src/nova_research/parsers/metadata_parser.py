"""Parser for catalog filter endpoints."""

from typing import Any
from nova_research.domain.metadata import City, LocationCatalog, Neighborhood, State


class MetadataParser:
    """Parses JSON responses from states, cities, and neighborhoods filter endpoints."""

    def parse(
        self,
        states_payload: dict[str, Any] | None = None,
        neighborhoods_payload: dict[str, Any] | None = None,
    ) -> LocationCatalog:
        """Construct LocationCatalog from raw states and neighborhoods payloads."""
        states = self._parse_states(states_payload)
        neighborhoods = self._parse_neighborhoods(neighborhoods_payload)
        return LocationCatalog(states=states, neighborhoods=neighborhoods)

    def _parse_states(self, payload: dict[str, Any] | None) -> list[State]:
        """Parse states and nested cities."""
        if not payload or "data" not in payload:
            return []
        return [self._to_state(s) for s in payload["data"] if isinstance(s, dict)]

    def _to_state(self, state_dict: dict[str, Any]) -> State:
        """Map raw state dictionary to domain State."""
        acronym = str(state_dict.get("acronym", ""))
        cities = self._parse_cities(state_dict.get("cities", []), acronym)
        return State(
            state_id=str(state_dict.get("id", "")),
            name=str(state_dict.get("name", "")),
            acronym=acronym,
            cities=cities,
        )

    def _parse_cities(self, raw_cities: Any, state_acronym: str) -> list[City]:
        """Map raw cities list to domain City instances."""
        if not isinstance(raw_cities, list):
            return []
        return [
            City(city_id=str(c.get("id", "")), name=str(c.get("name", "")), state_acronym=state_acronym)
            for c in raw_cities
            if isinstance(c, dict)
        ]

    def _parse_neighborhoods(self, payload: dict[str, Any] | None) -> list[Neighborhood]:
        """Parse neighborhoods list."""
        if not payload or "data" not in payload:
            return []
        return [
            Neighborhood(
                neighborhood_id=str(n.get("id", "")),
                name=str(n.get("name", "")),
            )
            for n in payload["data"]
            if isinstance(n, dict)
        ]
