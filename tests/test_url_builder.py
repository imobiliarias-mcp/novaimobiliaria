"""Unit tests for Tecimob UrlBuilder."""

from nova_research.infrastructure.url_builder import UrlBuilder


def test_url_builder_search_url() -> None:
    """Test construction of properties search endpoint URL."""
    builder = UrlBuilder()
    url = builder.build_search_url()
    assert url == "https://api-sites.tecimob.com.br/api/properties"


def test_url_builder_detail_url() -> None:
    """Test construction of property detail endpoint URL."""
    builder = UrlBuilder()
    url_id = builder.build_detail_url("a53048c2-0a25-4c51-9638-89395ede6d12")
    assert url_id == "https://api-sites.tecimob.com.br/api/properties/a53048c2-0a25-4c51-9638-89395ede6d12"

    url_ref = builder.build_detail_url("559")
    assert url_ref == "https://api-sites.tecimob.com.br/api/properties/559"


def test_url_builder_filter_endpoints() -> None:
    """Test construction of filter endpoint URLs."""
    builder = UrlBuilder()
    assert builder.build_types_filter_url() == "https://api-sites.tecimob.com.br/api/filters/types"
    assert builder.build_states_filter_url() == "https://api-sites.tecimob.com.br/api/filters/states"
    assert builder.build_neighborhoods_filter_url() == "https://api-sites.tecimob.com.br/api/filters/neighborhoods"
