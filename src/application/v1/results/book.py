import uuid_utils.compat as uuid

from src.application.v1.results.base import Result
from src.application.v1.results.category import CategoryResult


class BookResult(Result):
    uuid: uuid.UUID
    title: str
    author: str
    isbn: str
    price: float

    category: CategoryResult | None = None
