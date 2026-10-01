"""Standalone verification script for Nova Imobiliária rental research."""

import sys
from nova_research.client import NovaRentalClient
from nova_research.domain.criteria import SearchCriteria
from nova_research.domain.enums import PropertyType, SortOrder, TransactionType
from nova_research.domain.values import PageLimit, PageNumber


def main() -> int:
    """Run verification checks and print structured report."""
    print("=== Starting Nova Imobiliária Research Verification ===\n")
    client = NovaRentalClient()

    # 1. Target URL Search from prompt
    print("--- 1. Target URL Search (Alugar / Timóteo / Recent) ---")
    target_criteria = SearchCriteria(
        transaction=TransactionType.ALUGAR,
        location_slug="timoteo-mg",
        property_type=PropertyType.TODOS,
        sort=SortOrder.RECENT,
        page=PageNumber(1),
        limit=PageLimit(21),
    )
    results = client.search(target_criteria)
    meta = results.meta
    print(f"Total matching listings: {meta.total if meta else len(results)}")
    print(f"Page {meta.current_page if meta else 1} of {meta.total_pages if meta else 1}")
    for item in results[:5]:
        print(f"  [{item.identity.reference}] {item.title[:45]:<45} | {item.pricing.amount:<12} | {item.address_formatted}")

    # 2. Filtered Rental Search
    print("\n--- 2. Filtered Rental Search (Timóteo / 2 Bedrooms / Max R$ 2000) ---")
    filtered = client.search_rentals(
        city="timoteo-mg",
        bedrooms=2,
        max_price=2000,
        page=1,
    )
    print(f"Total matching filtered listings: {filtered.meta.total if filtered.meta else len(filtered)}")
    for item in filtered[:3]:
        print(f"  [{item.identity.reference}] {item.title[:45]:<45} | {item.pricing.amount:<12} | {item.rooms_summary}")

    # 3. Property Detail Retrieval
    print("\n--- 3. Property Detail Retrieval (Reference 559) ---")
    detail = client.get_details("559")
    print(f"Title: {detail.title}")
    print(f"Reference: {detail.identity.reference}")
    print(f"Price: {detail.pricing.amount}")
    print(f"Location: {detail.location.formatted}")
    print(f"Status: {detail.status} | Situation: {detail.situation}")
    print(f"Rooms details: {list(detail.rooms_details.keys())}")
    print(f"Areas details: {list(detail.areas_details.keys())}")

    # 4. Property Photos Gallery Retrieval
    print("\n--- 4. Property Photos Gallery Retrieval ---")
    gallery = detail.gallery
    print(f"Total photos retrieved: {len(gallery)}")
    for i, photo in enumerate(gallery[:3], 1):
        print(f"  Photo {i}: {photo.large_url}")

    # 5. Portal Location Catalog Discovery
    print("\n--- 5. Portal Location Catalog Discovery ---")
    catalog = client.get_locations()
    print(f"Total states in portal: {len(catalog.states)}")
    timoteo = catalog.find_city("timoteo-mg")
    if timoteo:
        print(f"City '{timoteo.name}' ({timoteo.city_id}) verified under {timoteo.state_acronym}.")
    print(f"Total indexed neighborhoods: {len(catalog.neighborhoods)}")

    print("\n=== All Verification Steps Completed Successfully ===")
    return 0


if __name__ == "__main__":
    sys.exit(main())
