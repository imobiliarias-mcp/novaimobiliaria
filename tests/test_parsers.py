"""Unit tests for SearchPageParser, PropertyDetailParser, and MetadataParser."""

from nova_research.parsers.detail_parser import PropertyDetailParser
from nova_research.parsers.metadata_parser import MetadataParser
from nova_research.parsers.search_parser import SearchPageParser


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
