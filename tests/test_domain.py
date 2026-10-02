"""Unit tests for domain values, criteria, listings, and properties."""

import pytest
from nova_research.domain.criteria import SearchCriteria
from nova_research.domain.enums import AreaType, PropertyType, SortOrder, TransactionType
from nova_research.domain.listing import (
    ListingCollection,
    ListingIdentity,
    ListingPricing,
    ListingSummary,
    PaginationMeta,
)
from nova_research.domain.metadata import City, LocationCatalog, Neighborhood, State
from nova_research.domain.property import Photo, PhotoGallery, PropertyDetail, PropertyLocation
from nova_research.domain.values import AreaRange, PageLimit, PageNumber, PriceRange, RoomCount


def test_price_range_validation_and_parameters() -> None:
    """Test price range validation and query parameter generation."""
    with pytest.raises(ValueError, match="negative"):
        PriceRange(minimum=-10)
    with pytest.raises(ValueError, match="exceed"):
        PriceRange(minimum=2000, maximum=1000)

    price = PriceRange(minimum=500, maximum=1500)
    params = price.query_parameters()
    assert params["filter[by_higher_than_price]"] == "500"
    assert params["filter[by_lower_than_price]"] == "1500"


def test_area_range_validation_and_parameters() -> None:
    """Test area range validation and query parameter generation."""
    with pytest.raises(ValueError, match="negative"):
        AreaRange(minimum=-5)
    with pytest.raises(ValueError, match="exceed"):
        AreaRange(minimum=300, maximum=100)

    area = AreaRange(minimum=50, maximum=250, area_type=AreaType.PRIVATE_AREA)
    params = area.query_parameters()
    assert params["filter[by_area][greater_equals]"] == "50"
    assert params["filter[by_area][lower_equals]"] == "250"
    assert params["filter[by_area][name]"] == "private_area"
    assert params["filter[by_area][measure]"] == "m²"


def test_room_count_validation_and_comparison() -> None:
    """Test room count validation and exact vs minimum formatting."""
    with pytest.raises(ValueError, match="negative"):
        RoomCount(count=-1)

    exact = RoomCount(count=2, is_minimum=False)
    k1, v1 = exact.query_parameter("bedroom")
    assert k1 == "filter[by_room_equals][bedroom]"
    assert v1 == "2"

    minimum = RoomCount(count=3, is_minimum=True)
    k2, v2 = minimum.query_parameter("suite")
    assert k2 == "filter[by_room_greater_equals][suite]"
    assert v2 == "3"


def test_page_number_and_limit_validation() -> None:
    """Test pagination bounds validation."""
    with pytest.raises(ValueError, match="greater than or equal to 1"):
        PageNumber(value=0)
    with pytest.raises(ValueError, match="greater than or equal to 1"):
        PageLimit(value=0)

    p = PageNumber(value=2)
    assert p.to_param() == "2"
    limit = PageLimit(value=10)
    assert limit.to_param() == "10"


def test_search_criteria_rental_factory() -> None:
    """Test SearchCriteria.create_rental factory and parameter mapping."""
    criteria = SearchCriteria.create_rental(
        city="timoteo-mg",
        property_type=PropertyType.APARTAMENTO,
        bedrooms=2,
        max_price=2000,
        page=2,
    )
    params = criteria.to_query_parameters()
    assert params["custom_query"] == "card"
    assert params["offset"] == "2"
    assert params["filter[transaction]"] == "2"
    assert params["filter[by_neighborhood_or_city_slug]"] == "timoteo-mg"
    assert params["filter[by_type_or_subtype_slug]"] == "apartamento"
    assert params["filter[by_lower_than_price]"] == "2000"
    assert params["filter[by_room_equals][bedroom]"] == "2"


def test_listing_collection_operations() -> None:
    """Test ListingCollection length, indexing, and iteration."""
    item = ListingSummary(
        identity=ListingIdentity("123", "ref1"),
        title="Apartamento Teste",
        pricing=ListingPricing("R$ 1.000,00"),
        address_formatted="Centro, Timóteo",
        rooms_summary="2 quartos",
        primary_area="60 m²",
        thumbnail_url="http://example.com/img.jpg",
        canonical_path="imovel/123",
    )
    meta = PaginationMeta(total=1, per_page=10, current_page=1, total_pages=1)
    col = ListingCollection(items=[item], meta=meta)
    assert len(col) == 1
    assert col[0].identity.property_id == "123"
    assert col.first() == item
    assert not meta.has_next_page


def test_listing_collection_serializes_items_and_pagination() -> None:
    """Serialize every typed listing field and preserve pagination metadata."""
    listing = ListingSummary(
        identity=ListingIdentity("uuid-123", "ref-123"),
        title="Apartamento Teste",
        pricing=ListingPricing("R$ 1.000,00", "R$ 1.000,00"),
        address_formatted="Centro, Timóteo",
        rooms_summary="2 quartos",
        primary_area="60 m²",
        thumbnail_url="https://images.example/thumb.jpg",
        canonical_path="imovel/123",
        url="https://jnovaimobiliaria.com.br/imovel/123",
    )
    meta = PaginationMeta(total=6, per_page=2, current_page=2, total_pages=3)
    collection = ListingCollection(items=[listing, listing], meta=meta)

    serialized = collection.to_dictionary()

    assert len(serialized["items"]) == 2
    assert serialized["items"][0]["url"] == listing.url
    assert serialized["items"][0]["canonical_path"] == listing.canonical_path
    assert serialized["items"][0]["identity"]["property_id"] == "uuid-123"
    assert serialized["items"][0]["pricing"]["total_price"] == "R$ 1.000,00"
    assert serialized["returned_count"] == 2
    assert serialized["meta"] == {
        "total": 6,
        "per_page": 2,
        "current_page": 2,
        "total_pages": 3,
    }


def test_empty_listing_collection_serializes_zero_count() -> None:
    """Serialize zero results while retaining the absent pagination metadata."""
    serialized = ListingCollection().to_dictionary()

    assert serialized["items"] == []
    assert serialized["returned_count"] == 0
    assert serialized["meta"] is None


def test_photo_gallery_operations() -> None:
    """Test PhotoGallery collection methods."""
    photo1 = Photo("p1", "http://example.com/large1.jpg", "http://example.com/med1.jpg")
    photo2 = Photo("p2", "http://example.com/large2.jpg", "http://example.com/med2.jpg")
    gallery = PhotoGallery(photos=[photo1, photo2])
    assert len(gallery) == 2
    assert gallery.first_photo() == photo1
    assert gallery.large_urls() == ["http://example.com/large1.jpg", "http://example.com/large2.jpg"]


def test_location_catalog_lookup() -> None:
    """Test LocationCatalog municipality and neighborhood lookup."""
    city = City(city_id="timoteo-mg", name="Timóteo", state_acronym="MG")
    state = State(state_id="MG", name="Minas Gerais", acronym="MG", cities=[city])
    neigh = Neighborhood(neighborhood_id="timoteo-mg-centro", name="Centro")
    catalog = LocationCatalog(states=[state], neighborhoods=[neigh])

    assert catalog.find_city("timoteo-mg") == city
    assert catalog.find_city("non-existent") is None
    assert catalog.find_neighborhood("timoteo-mg-centro") == neigh
    assert catalog.find_neighborhood("unknown") is None
