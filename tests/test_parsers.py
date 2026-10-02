"""Unit tests for SearchPageParser, PropertyDetailParser, and MetadataParser."""

import pytest

from nova_research.domain.listing import InvalidListingUrlError
from nova_research.parsers.detail_parser import PropertyDetailParser
from nova_research.parsers.metadata_parser import MetadataParser
from nova_research.parsers.search_parser import SearchPageParser


def _listing_payload(public_path: str) -> dict:
    """Build one minimal search result with the supplied card URL."""
    return {
        "data": [{"id": "item-id-608", "reference": "608", "url": public_path}]
    }


@pytest.mark.parametrize(
    ("card_url", "expected_url"),
    [
        (
            "https://jnovaimobiliaria.com.br/imovel/absolute/608",
            "https://jnovaimobiliaria.com.br/imovel/absolute/608",
        ),
        ("/imovel/relative/608", "https://jnovaimobiliaria.com.br/imovel/relative/608"),
        (
            "//jnovaimobiliaria.com.br/imovel/protocol-relative/608",
            "https://jnovaimobiliaria.com.br/imovel/protocol-relative/608",
        ),
        ("?id=608", "https://jnovaimobiliaria.com.br/?id=608"),
    ],
)
def test_search_parser_resolves_public_card_urls(card_url: str, expected_url: str) -> None:
    """Resolve public URLs while retaining the source canonical path."""
    listing = SearchPageParser().parse(_listing_payload(card_url))[0]

    assert listing.url == expected_url
    assert listing.canonical_path == card_url


def test_search_parser_rejects_documented_api_url_with_identity() -> None:
    """Reject an API endpoint as a property page with the listing ID in context."""
    payload = {
        "data": [
            {
                "id": "uuid-1",
                "url": "https://api-sites.tecimob.com.br/api/properties/uuid-1",
            }
        ]
    }

    with pytest.raises(InvalidListingUrlError, match="uuid-1"):
        SearchPageParser().parse(payload)


def test_search_parser_uses_injected_public_base_url() -> None:
    """Resolve relative card links using the configured public site origin."""
    parser = SearchPageParser(public_base_url="https://public.example/")

    listing = parser.parse(_listing_payload("/imovel/configured/608"))[0]

    assert listing.url == "https://public.example/imovel/configured/608"


@pytest.mark.parametrize("card_url", ["javascript:alert(1)", ""])
def test_search_parser_rejects_unrecoverable_public_url(card_url: str) -> None:
    """Reject invalid or absent URLs with property identity in the error."""
    with pytest.raises(InvalidListingUrlError, match="item-id-608"):
        SearchPageParser().parse(_listing_payload(card_url))


@pytest.mark.parametrize(
    "card_url",
    [
        "https://bad host.example/imovel/listing/608",
        "https://user:password@jnovaimobiliaria.com.br/imovel/listing/608",
        "https://jnovaimobiliaria.com.br:invalid/imovel/listing/608",
        "https://[invalid]/imovel/listing/608",
        "https://api-sites.tecimob.com.br/api/properties/uuid-1",
        "https://imagens.tecimob.com.br/property-photo.jpg",
        "https://jnovaimobiliaria.com.br/alugar/imoveis/timoteo-mg?offset=1",
    ],
)
def test_search_parser_rejects_invalid_public_property_urls(card_url: str) -> None:
    """Reject malformed authorities and non-property endpoint URLs."""
    with pytest.raises(InvalidListingUrlError, match="item-id-608"):
        SearchPageParser().parse(_listing_payload(card_url))


@pytest.mark.parametrize(
    "public_base_url",
    [
        "https://bad host.example/",
        "https://user:password@public.example/",
        "https://public.example:invalid/",
    ],
)
def test_search_parser_rejects_malformed_public_base(public_base_url: str) -> None:
    """Reject malformed origin configuration before parsing listings."""
    with pytest.raises(ValueError, match="public base URL"):
        SearchPageParser(public_base_url=public_base_url)


def test_search_page_parser_with_payload() -> None:
    """Test parsing search response dictionary."""
    parser = SearchPageParser()
    payload = {
        "meta": {
            "pagination": {
                "total": 19,
                "per_page": 21,
                "current_page": 1,
                "total_pages": 1,
            }
        },
        "data": [
            {
                "id": "item-uuid-1",
                "reference": "559",
                "title_formatted": "Sala comercial em Timóteo",
                "price": "R$2.800,00",
                "total_price": "R$2.800,00",
                "address": {"formatted": "Centro - Timóteo/MG"},
                "rooms": {
                    "kitchen": {"title_formated": "1 Cozinha", "value": 1},
                    "washbasin": {"title_formated": "1 Lavabo", "value": 1},
                },
                "areas": {
                    "primary_area": {"value": "81", "measure": "m²"}
                },
                "images_extra": [
                    {
                        "id": "img-1",
                        "file_url": {
                            "large": "https://img.tecimob/large.jpg",
                            "medium": "https://img.tecimob/med.jpg",
                        }
                    }
                ],
                "url": "sala-comercial-559",
            }
        ],
    }

    collection = parser.parse(payload)
    assert len(collection) == 1
    assert collection.meta is not None
    assert collection.meta.total == 19
    item = collection[0]
    assert item.identity.property_id == "item-uuid-1"
    assert item.identity.reference == "559"
    assert item.pricing.amount == "R$2.800,00"
    assert item.address_formatted == "Centro - Timóteo/MG"
    assert "1 Cozinha" in item.rooms_summary
    assert item.primary_area == "81 m²"
    assert item.thumbnail_url == "https://img.tecimob/med.jpg"
    assert item.canonical_path == "sala-comercial-559"
    assert item.url == "https://jnovaimobiliaria.com.br/sala-comercial-559"


def test_property_detail_parser() -> None:
    """Test parsing single property detail response dictionary."""
    parser = PropertyDetailParser()
    payload = {
        "data": {
            "id": "uuid-detail-1",
            "reference": "559",
            "title_formatted": "Sala comercial Duplex",
            "description": "<p>Aluguel excelente sala</p>",
            "price": "R$2.800,00",
            "address": {"formatted": "Centro - Timóteo/MG"},
            "rooms": {"kitchen": {"title_formated": "1 Cozinha"}},
            "areas": {"primary_area": {"value": "81", "measure": "m²"}},
            "images_extra": [
                {
                    "id": "photo-1",
                    "file_url": {
                        "large": "https://img.tecimob/photo1_lg.jpg",
                        "medium": "https://img.tecimob/photo1_md.jpg",
                    }
                }
            ],
            "url": "sala-559",
            "status": "Disponível",
            "situation": "Usado",
        }
    }

    detail = parser.parse(payload)
    assert detail.identity.property_id == "uuid-detail-1"
    assert detail.identity.reference == "559"
    assert detail.pricing.amount == "R$2.800,00"
    assert detail.location.formatted == "Centro - Timóteo/MG"
    assert len(detail.gallery) == 1
    assert detail.gallery[0].large_url == "https://img.tecimob/photo1_lg.jpg"
    assert detail.status == "Disponível"
    assert detail.situation == "Usado"


def test_metadata_parser() -> None:
    """Test parsing states and neighborhoods filter responses."""
    parser = MetadataParser()
    states_payload = {
        "data": [
            {
                "id": "MG",
                "name": "Minas Gerais",
                "acronym": "MG",
                "cities": [
                    {"id": "timoteo-mg", "name": "Timóteo"},
                    {"id": "ipatinga-mg", "name": "Ipatinga"},
                ]
            }
        ]
    }
    neighs_payload = {
        "data": [
            {"id": "timoteo-mg-centro", "name": "Centro"},
            {"id": "timoteo-mg-timirim", "name": "Timirim"},
        ]
    }

    catalog = parser.parse(states_payload, neighs_payload)
    assert len(catalog.states) == 1
    assert catalog.find_city("timoteo-mg") is not None
    assert catalog.find_city("timoteo-mg").name == "Timóteo"
    assert catalog.find_neighborhood("timoteo-mg-centro") is not None
    assert catalog.find_neighborhood("timoteo-mg-centro").name == "Centro"
