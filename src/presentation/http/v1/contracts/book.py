from decimal import Decimal
from uuid import UUID

import uuid_utils.compat as uuid

from src.presentation.http.common.contract import Contract
from src.presentation.http.v1.contracts.short import CategoryShort


class Book(Contract):
    uuid: uuid.UUID
    title: str
    upc: str
    price: Decimal
    stock_count: int
    rating: int
    description: str
    page_url: str
    image_url: str
    category_uuid: UUID

    category: CategoryShort | None = None


class SelectBooks(Contract):
    category_uuid: uuid.UUID | None = None
    category_name: str | None = None
    price_from: Decimal | None = None
    price_to: Decimal | None = None
    rating: int | None = None
    in_stock: bool | None = None
