"""URL builder for constructing Tecimob API endpoint addresses."""

from urllib.parse import urljoin
from nova_research.domain.criteria import SearchCriteria


class UrlBuilder:
    """Constructs API endpoint URLs for Nova Imobiliária research."""

    API_BASE = "https://api-sites.tecimob.com.br/api/"

    def __init__(self, base_url: str = API_BASE) -> None:
        """Initialize URL builder with base API endpoint."""
        self._base = base_url

    def build_search_url(self) -> str:
        """Return properties search endpoint URL."""
        return urljoin(self._base, "properties")

    def build_detail_url(self, property_id_or_reference: str) -> str:
        """Construct property detail endpoint URL for a given ID or reference."""
        cleaned_id = property_id_or_reference.strip("/")
        return urljoin(self._base, f"properties/{cleaned_id}")

    def build_types_filter_url(self) -> str:
        """Return endpoint URL for property types filter."""
        return urljoin(self._base, "filters/types")

    def build_states_filter_url(self) -> str:
        """Return endpoint URL for states and cities filter."""
        return urljoin(self._base, "filters/states")

    def build_neighborhoods_filter_url(self) -> str:
        """Return endpoint URL for neighborhoods filter."""
        return urljoin(self._base, "filters/neighborhoods")
