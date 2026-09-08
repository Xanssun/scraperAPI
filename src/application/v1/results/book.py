from __future__ import annotations

from decimal import Decimal
from typing import TYPE_CHECKING

import uuid_utils.compat as uuid

from src.application.v1.results.base import Result

if TYPE_CHECKING:
    from src.application.v1.results.category import CategoryShortResult


class BookShortResult(Result):
    uuid: uuid.UUID
    title: str
    upc: str
    price: Decimal


class BookResult(BookShortResult):
    stock_count: int
    rating: int
    description: str
    page_url: str
    image_url: str
    category_uuid: uuid.UUID

    category: CategoryShortResult | None = None
