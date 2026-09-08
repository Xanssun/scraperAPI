from __future__ import annotations

from typing import TYPE_CHECKING

import uuid_utils.compat as uuid

from src.application.v1.results.base import Result

if TYPE_CHECKING:
    from src.application.v1.results.book import BookShortResult


class CategoryShortResult(Result):
    uuid: uuid.UUID
    name: str


class CategoryResult(CategoryShortResult):
    books: list[BookShortResult] | None = None
