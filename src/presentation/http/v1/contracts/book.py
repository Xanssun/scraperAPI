from decimal import Decimal
from typing import Annotated
from uuid import UUID

import uuid_utils.compat as uuid
from pydantic import Field

from src.presentation.http.common.contract import Contract
from src.presentation.http.v1.contracts.short import CategoryShort

Price = Annotated[
    Decimal,
    Field(
        ge=Decimal("0"),
        max_digits=10,
        decimal_places=2,
        examples=[Decimal("51.77")],
    ),
]

class Book(Contract):
    uuid: uuid.UUID
    title: str
    upc: str
    price: Price
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
