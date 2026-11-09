"""Unit tests for NovaMcpAdapter."""

from scripts.mcp.tools import NovaMcpAdapter


class DummyClient:
    """Dummy client for testing Nova MCP adapter."""

    def search_rentals(self, **kwargs):
        class DummyListing:
            property_id = "555"
            code = "NV01"
            title = "Apto Nova Timóteo"
            price_formatted = "R$ 1.300"
            url = "https://www.novaimobiliaria.com/imovel/555"
            class location:
                neighborhood = "Funcionários"
                city = "Timóteo"
            class specs:
                bedrooms = 2
                bathrooms = 1
        class DummyCollection(list):
            pass
        return DummyCollection([DummyListing()])

    def get_details(self, ref):
        class DummyDetail:
            property_id = "555"
            code = "NV01"
            title = "Apto Nova Timóteo"
            description = "Excelente localização"
            price_formatted = "R$ 1.300"
            url = "https://www.novaimobiliaria.com/imovel/555"
            gallery = ["https://www.novaimobiliaria.com/foto1.jpg"]
            class location:
                neighborhood = "Funcionários"
                city = "Timóteo"
            class specs:
                bedrooms = 2
                bathrooms = 1
                parking_spaces = 1
                area = 80.0
        return DummyDetail()

    def get_locations(self):
        class DummyLocations:
            cities = []
            neighborhoods = []
        return DummyLocations()


def test_mcp_adapter_provider_info():
    """Test MCP provider metadata."""
    adapter = NovaMcpAdapter(client=DummyClient())
    info = adapter.get_provider_info()
    assert info["provider_name"] == "novaimobiliaria"
    assert "search_rentals" in info["supported_operations"]


def test_mcp_adapter_search_rentals():
    """Test MCP search tool execution."""
    adapter = NovaMcpAdapter(client=DummyClient())
    res = adapter.search_rentals(city="Timóteo", bedrooms=2, max_price=1500.0)
    assert isinstance(res, dict)
    assert res["provider"] == "novaimobiliaria"
    assert len(res["listings"]) == 1


def test_mcp_adapter_property_detail():
    """Test MCP property detail tool execution."""
    adapter = NovaMcpAdapter(client=DummyClient())
    detail = adapter.get_property_detail("555")
    assert isinstance(detail, dict)
    assert detail["title"] == "Apto Nova Timóteo"


class _Identity:
    def __init__(self, property_id: str, reference: str) -> None:
        self.property_id = property_id
        self.reference = reference


class _RealShapedClient:
    """Mirrors the domain objects the parsers really return: identity lives under .identity."""

    def search_rentals(self, **kwargs):
        class Summary:
            identity = _Identity("555", "NV01")
            title = "Apto Nova Timóteo"
            thumbnail_url = "https://cdn.test/nova-thumb.jpg"

            class pricing:
                amount = "R$ 1.300"

            url = "https://www.novaimobiliaria.com/imovel/555"

        return [Summary()]

    def get_details(self, ref):
        class Photo:
            large_url = "https://cdn.test/nova-large.jpg"
            medium_url = "https://cdn.test/nova-medium.jpg"

        class Photo2:
            large_url = ""
            medium_url = "https://cdn.test/nova-medium-only.jpg"

        class Gallery:
            photos = [Photo(), Photo2()]

        class Detail:
            identity = _Identity("555", "NV01")
            title = "Apto Nova Timóteo"
            description = "<p>Sol da manhã</p>"
            gallery = Gallery()
            url = "https://www.novaimobiliaria.com/imovel/555"

        return Detail()


def test_search_items_carry_identifiers_and_thumbnail_from_identity():
    adapter = NovaMcpAdapter(client=_RealShapedClient())
    item = adapter.search_rentals()["listings"][0]
    assert item["code"] == "NV01"
    assert item["id"] == "555"
    assert item["media_url"] == "https://cdn.test/nova-thumb.jpg"


def test_detail_photos_are_urls_not_objects():
    adapter = NovaMcpAdapter(client=_RealShapedClient())
    detail = adapter.get_property_detail("NV01")
    assert detail["photos"] == ["https://cdn.test/nova-large.jpg", "https://cdn.test/nova-medium-only.jpg"]
    assert detail["code"] == "NV01"
