import uuid_utils.compat as uuid

from src.presentation.http.common.contract import Contract
from src.presentation.http.v1.contracts.short import BookShort


class Category(Contract):
    uuid: uuid.UUID
    name: str

    books: list[BookShort] | None = None


class SelectCategories(Contract):
    name: str | None = None
