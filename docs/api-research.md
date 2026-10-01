# Reverse-Engineered API Specification: Nova Imobiliária

## 1. Overview & Architecture

Nova Imobiliária (`https://jnovaimobiliaria.com.br`) is a real estate portal operating in the Vale do Aço region (Timóteo, Coronel Fabriciano, Ipatinga, MG).

The website frontend is built on **Next.js** (React) and communicates directly with a multi-tenant real estate SaaS backend provided by **Tecimob** (`https://api-sites.tecimob.com.br/api/`). While the frontend renders initial page shells, property searches, listings, filtering, pagination, and detail views are completely driven by client-side JSON REST APIs.

### 1.1 Authentication & Multi-Tenant Security
- **Authentication**: **None required** for public search and property viewing flows. There are no cookies, session tokens, or API keys required.
- **Tenant Identification Header**: The API requires a tenant routing header:
  ```http
  x-domain: jnovaimobiliaria.com.br
  ```
  Requests lacking this header or specifying an invalid domain return `HTTP 401 Unauthorized` (`Symfony\Component\HttpKernel\Exception\UnauthorizedHttpException: Não autorizado!`).
- **HTTP Methods**: All search, filter, pagination, catalog, and property detail operations strictly utilize `GET`.
- **Content Type**: `application/json` for both request `Accept` header and server responses.

---

## 2. Rental Search Endpoints

### 2.1 Properties Listing & Search Endpoint

```http
GET https://api-sites.tecimob.com.br/api/properties?{query_parameters} HTTP/1.1
Host: api-sites.tecimob.com.br
x-domain: jnovaimobiliaria.com.br
Accept: application/json
User-Agent: Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36
```

---

## 3. Request Parameters & Filter Behavior

The search endpoint accepts parameter bundles configuring query mode, pagination, sorting, and multi-field criteria:

### 3.1 Core Control Parameters
| Parameter | Type | Required | Example | Description |
| :--- | :--- | :--- | :--- | :--- |
| `custom_query` | `string` | Recommended | `card` | Formats payload for card listings (includes pricing, summary rooms, primary area, and image array). |
| `sort` | `string` | Optional | `-created_at,id` | Sort ordering (see Sort Options below). |
| `offset` | `integer` | Optional | `1` | **1-indexed page number** (e.g. `1`, `2`, `3`). |
| `limit` | `integer` | Optional | `21` | Page size (number of properties returned per page). |

### 3.2 Filter Parameters (`filter[...]`)
| Parameter | Type | Example | Description / Logic |
| :--- | :--- | :--- | :--- |
| `filter[transaction]` | `string` | `2` | Transaction type:<br>• `1`: Comprar (Sales)<br>• `2`: Alugar (Rentals)<br>• `3`: Temporada (Seasonal) |
| `filter[by_neighborhood_or_city_slug]` | `string` | `timoteo-mg` | City or neighborhood slug (e.g. `timoteo-mg`, `timoteo-mg-centro`, `coronel-fabriciano-mg`). |
| `filter[by_type_or_subtype_slug]` | `string` | `apartamento` | Property type category (e.g. `apartamento`, `casa`, `sala-comercial`, `terreno`). |
| `filter[by_higher_than_price]` | `integer` | `1000` | Minimum price constraint in BRL. |
| `filter[by_lower_than_price]` | `integer` | `2500` | Maximum price constraint in BRL. |
| `filter[by_room_equals][bedroom]` | `integer` | `2` | Exact bedroom count match. |
| `filter[by_room_greater_equals][bedroom]` | `integer` | `2` | Minimum bedroom count match ("N or more"). |
| `filter[by_room_equals][suite]` | `integer` | `1` | Exact suite count match. |
| `filter[by_room_greater_equals][suite]` | `integer` | `1` | Minimum suite count match. |
| `filter[by_room_equals][garage]` | `integer` | `1` | Exact parking spaces match. |
| `filter[by_room_greater_equals][garage]` | `integer` | `1` | Minimum parking spaces match. |
| `filter[by_area][name]` | `string` | `total_area` | Area category (`total_area`, `private_area`, `built_area`). |
| `filter[by_area][measure]` | `string` | `m²` | Area unit of measurement (`m²`, `ha`). |
| `filter[by_area][greater_equals]` | `integer` | `50` | Minimum area in specified unit. |
| `filter[by_area][lower_equals]` | `integer` | `200` | Maximum area in specified unit. |

### 3.3 Sort Options
- `-created_at,id`: Most recently published properties first (default on portal).
- `-is_price_shown,by_calculated_price,id`: Price low to high.
- `-is_price_shown,-by_calculated_price,id`: Price high to low.

---

## 4. Pagination Behavior

- **Page Indicator**: `offset` is a **1-indexed page counter**, not a record offset.
  - Page 1: `offset=1`
  - Page 2: `offset=2`
  - Page 3: `offset=3`
- **Page Size**: `limit` configures the number of records returned per page (default `21`).
- **Response Metadata**: The API returns pagination metadata under `meta.pagination`:
  ```json
  "meta": {
    "pagination": {
      "total": 19,
      "per_page": 21,
      "current_page": 1,
      "total_pages": 1
    }
  }
  ```
- **Out-of-Bounds Behavior**:
  - Requesting `offset=999` returns HTTP 200 with an empty array: `"data": []`.
  - Termination condition: `current_page >= total_pages` or `len(data) == 0`.

---

## 5. Search Results Card Parsing

When `custom_query=card` is supplied, each item in the `data` array represents a listing card with pre-computed display attributes:

### 5.1 Card Structure Sample
```json
{
  "id": "a53048c2-0a25-4c51-9638-89395ede6d12",
  "reference": "559",
  "transaction": "ALUGUEL",
  "price": "R$2.800,00",
  "total_price": "R$2.800,00",
  "title_formatted": "Sala comercial Duplex em Centro, Timóteo/MG",
  "address": {
    "formatted": "Centro - Timóteo/MG"
  },
  "rooms": {
    "kitchen": {
      "title": "Cozinha",
      "value": 1,
      "title_formated": "1 Cozinha"
    },
    "washbasin": {
      "title": "Lavabo",
      "value": 1,
      "title_formated": "1 Lavabo"
    }
  },
  "areas": {
    "primary_area": {
      "name": "private_area",
      "title": "Área Privativa",
      "value": "81",
      "measure": "m²"
    }
  },
  "images_extra": [
    {
      "id": "1d7ff6bd-ad63-4115-a0a1-adb723572915",
      "file_url": {
        "large": "https://imagens.tecimob.com.br/.../1d7ff6bd...NQtf.jpg",
        "medium": "https://imagens.tecimob.com.br/.../outside/1d7ff6bd...NQtf.webp"
      }
    }
  ],
  "url": "sala-comercial-para-alugar-no-bairro-centro-em-timoteo-mg/559"
}
```

### 5.2 Field Extraction Matrix
| Domain Field | JSON Path | Example Value |
| :--- | :--- | :--- |
| `property_id` | `item.id` | `a53048c2-0a25-4c51-9638-89395ede6d12` |
| `reference` | `item.reference` | `559` |
| `title` | `item.title_formatted` | `Sala comercial Duplex em Centro, Timóteo/MG` |
| `price_text` | `item.price` | `R$2.800,00` |
| `address_formatted` | `item.address.formatted` | `Centro - Timóteo/MG` |
| `rooms_summary` | Join `item.rooms.*.title_formated` | `1 Cozinha, 1 Lavabo` |
| `primary_area` | `item.areas.primary_area.value` + `measure` | `81 m²` |
| `thumbnail_url` | `item.images_extra[0].file_url.medium` | `https://imagens.tecimob.com.br/.../webp` |
| `canonical_url` | `item.url` | `sala-comercial-para-alugar-no-bairro-centro.../559` |

---

## 6. Property Detail Retrieval

Full property details are retrieved via direct ID or reference code lookup.

### 6.1 Detail Endpoint
```http
GET https://api-sites.tecimob.com.br/api/properties/{id_or_reference} HTTP/1.1
Host: api-sites.tecimob.com.br
x-domain: jnovaimobiliaria.com.br
Accept: application/json
```
- **Lookup by UUID**: e.g. `/api/properties/a53048c2-0a25-4c51-9638-89395ede6d12`
- **Lookup by Reference**: e.g. `/api/properties/559`
- **404 Behavior**: Non-existent properties return HTTP 404.

### 6.2 Full Detail Payload Contents
The response contains comprehensive property data under `"data"`:
- `title_formatted`: Formatted display title.
- `description`: HTML description with amenities and property remarks.
- `price` / `total_price` / `condominium_price` / `taxes_price`.
- `address`: Formatted and structured address.
- `rooms`: Complete breakdown of rooms (dormitórios, suítes, banheiros, garagens cobertas, copas, salas).
- `areas`: Total, private, and built areas with metrics.
- `status`: Availability status (e.g. `Disponível`).
- `situation`: Property condition (e.g. `Usado`, `Breve lançamento`).
- `images_extra`: Array of high-resolution photos with `large` and `medium` webp/jpeg URLs.

---

## 7. Supporting Filter & Catalog Endpoints

The API provides supporting catalog endpoints for building search filters and UI lookups:

| Endpoint | Method | Purpose | Response Content |
| :--- | :--- | :--- | :--- |
| `/api/filters/types?sort=order&filter[having_properties]=true` | `GET` | Property types | List of types (`apartamento`, `casa`, `loja`, etc.) and their nested subtypes. |
| `/api/filters/states?sort=acronym` | `GET` | States & Cities | States (`BA`, `ES`, `MG`, `SP`) and all nested municipalities with IDs and names. |
| `/api/filters/neighborhoods?sort=slug` | `GET` | Neighborhoods | 68 indexed neighborhoods across covered municipalities. |
| `/api/properties/transactions` | `GET` | Transaction types | `comprar` (`_id: 1`), `alugar` (`_id: 2`), `temporada` (`_id: 3`). |
| `/api/properties/areas` | `GET` | Area categories | `built_area`, `total_area`, `private_area`, measures (`m²`, `ha`). |
| `/api/properties/situations` | `GET` | Property conditions | `Usado`, `Novo`, `Em construção`, `Breve lançamento`. |
| `/api/properties/furnitures` | `GET` | Furnishing options | `Sem mobília`, `Semi-mobiliado`, `Mobiliado`. |

---

## 8. Target URL Reproduction Analysis

### Target URL from Prompt
`https://jnovaimobiliaria.com.br/alugar/imoveis/timoteo-mg?sort=-created_at%2Cid&offset=1&limit=21&typeArea=total_area&floorComparision=equals`

### Query Parameter Decomposition
1. **Frontend Path**: `/alugar/imoveis/timoteo-mg`
   - `transaction`: `alugar` $\to$ maps to backend filter `filter[transaction]=2`.
   - `type`: `imoveis` $\to$ default category for all types.
   - `address`: `timoteo-mg` $\to$ maps to backend filter `filter[by_neighborhood_or_city_slug]=timoteo-mg`.
2. **Frontend Query String**:
   - `sort=-created_at,id` $\to$ maps directly to `sort=-created_at,id`.
   - `offset=1` $\to$ maps to `offset=1` (page 1).
   - `limit=21` $\to$ maps to `limit=21` (21 listings).
   - `typeArea=total_area` $\to$ maps to `filter[by_area][name]=total_area`.
   - `floorComparision=equals` $\to$ frontend floor comparison setting.

### Exact API Call Equivalent
```http
GET https://api-sites.tecimob.com.br/api/properties?custom_query=card&sort=-created_at%2Cid&offset=1&limit=21&filter%5Btransaction%5D=2&filter%5Bby_neighborhood_or_city_slug%5D=timoteo-mg HTTP/1.1
Host: api-sites.tecimob.com.br
x-domain: jnovaimobiliaria.com.br
Accept: application/json
```
- Total listings matching this search: **19 properties**.

---

## 9. Python MCP Client Integration Summary

The reverse-engineered endpoints are encapsulated inside `nova_research`:

```python
from nova_research import NovaRentalClient, PropertyType, SearchCriteria

client = NovaRentalClient()

# 1. Reproduce target prompt search (Rentals in Timóteo)
rentals = client.search_rentals(
    city="timoteo-mg",
    property_type=PropertyType.TODOS,
    page=1,
)
print(f"Total matching: {rentals.meta.total}")
for listing in rentals:
    print(listing.identity.reference, listing.title, listing.pricing.amount)

# 2. Retrieve property details
detail = client.get_details("559")
print(detail.title, detail.pricing.amount, detail.location.formatted)

# 3. Access property photo gallery
for photo in detail.gallery:
    print("Photo URL:", photo.large_url)

# 4. Access location catalog
catalog = client.get_locations()
timoteo = catalog.find_city("timoteo-mg")
print(f"City: {timoteo.name}, State: {timoteo.state_acronym}")
```
