import uuid_utils.compat as uuid

from src.application.v1.results.base import Result
from src.application.v1.results.book import BookResult


class CategoryResult(Result):
    uuid: uuid.UUID
    name: str

    books: list[BookResult] | None = None
