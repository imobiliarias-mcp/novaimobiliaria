"""Live integration tests against live Tecimob API for Nova Imobiliária."""

import pytest
from nova_research.client import NovaRentalClient
from nova_research.domain.criteria import SearchCriteria
from nova_research.domain.enums import PropertyType, SortOrder, TransactionType
from nova_research.domain.values import PageLimit, PageNumber


@pytest.fixture
def client() -> NovaRentalClient:
    """Fixture providing configured NovaRentalClient."""
    return NovaRentalClient()


def test_live_target_prompt_url_search(client: NovaRentalClient) -> None:
    """Test reproducing the prompt target rental search flow."""
    criteria = SearchCriteria(
        transaction=TransactionType.ALUGAR,
        location_slug="timoteo-mg",
        property_type=PropertyType.TODOS,
        sort=SortOrder.RECENT,
        page=PageNumber(value=1),
        limit=PageLimit(value=21),
    )
    listings = client.search(criteria)
    assert len(listings) > 0
    assert listings.meta is not None
    assert listings.meta.total > 0
    assert listings.meta.current_page == 1

    first = listings.first()
    assert first is not None
    assert first.identity.property_id != ""
    assert first.identity.reference != ""
    assert first.pricing.amount.startswith("R$")


def test_live_rental_property_details(client: NovaRentalClient) -> None:
    """Test retrieving live property details and photo gallery for reference 559."""
    detail = client.get_details("559")
    assert detail.identity.reference == "559"
    assert "Sala" in detail.title or "comercial" in detail.title or "Centro" in detail.title
    assert "Centro" in detail.location.formatted
    assert len(detail.gallery) > 0
    first_photo = detail.gallery.first_photo()
    assert first_photo is not None
    assert "https://imagens.tecimob.com.br" in first_photo.large_url


def test_live_pagination_behavior(client: NovaRentalClient) -> None:
    """Test pagination behavior with limit=3 across page 1 and page 2."""
    p1 = client.search(
        SearchCriteria(
            transaction=TransactionType.ALUGAR,
            location_slug="timoteo-mg",
            page=PageNumber(1),
            limit=PageLimit(3),
        )
    )
    p2 = client.search(
        SearchCriteria(
            transaction=TransactionType.ALUGAR,
            location_slug="timoteo-mg",
            page=PageNumber(2),
            limit=PageLimit(3),
        )
    )
    assert len(p1) == 3
    assert len(p2) == 3
    refs1 = [item.identity.reference for item in p1]
    refs2 = [item.identity.reference for item in p2]
    # Verify no overlap between pages
    assert set(refs1).isdisjoint(set(refs2))


def test_live_location_catalog(client: NovaRentalClient) -> None:
    """Test retrieving geographic location catalog."""
    catalog = client.get_locations()
    assert len(catalog.states) > 0
    timoteo = catalog.find_city("timoteo-mg")
    assert timoteo is not None
    assert timoteo.name == "Timóteo"
    assert timoteo.state_acronym == "MG"
