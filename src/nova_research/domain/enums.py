"""Domain enumerations for rental and property research."""

from enum import Enum


class TransactionType(str, Enum):
    """Transaction purpose identifiers defined by Tecimob."""

    COMPRAR = "1"
    ALUGAR = "2"
    TEMPORADA = "3"


class PropertyType(str, Enum):
    """Common property types in the portal catalog."""

    TODOS = "todos"
    APARTAMENTO = "apartamento"
    CASA = "casa"
    SALA_COMERCIAL = "sala-comercial"
    LOTE = "loteamento"
    TERRENO = "terreno"
    SITIO = "sitio"
    CHACARA = "chacara"
    LOJA = "loja"
    GALPAO = "pavilhao-galpao"
    PONTO_COMERCIAL = "ponto-comercial"


class SortOrder(str, Enum):
    """Supported sort criteria for property queries."""

    RECENT = "-created_at,id"
    PRICE_ASC = "-is_price_shown,by_calculated_price,id"
    PRICE_DESC = "-is_price_shown,-by_calculated_price,id"


class AreaType(str, Enum):
    """Supported area categories for filtering."""

    TOTAL_AREA = "total_area"
    PRIVATE_AREA = "private_area"
    BUILT_AREA = "built_area"
