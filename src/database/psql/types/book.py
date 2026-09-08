from decimal import Decimal
from typing import Literal, TypedDict

import uuid_utils.compat as uuid

BookLoads = Literal["category"]


class CreateBookType(TypedDict):
    title: str
    upc: str
    price: Decimal
    stock_count: int
    rating: int
    description: str
    page_url: str
    image_url: str
    category_uuid: uuid.UUID


class UpdateBookType(TypedDict, total=False):
    title: str
    price: Decimal
    stock_count: int
    rating: int
    description: str
    page_url: str
    image_url: str
    category_uuid: uuid.UUID
