from decimal import Decimal

import uuid_utils.compat as uuid

from src.presentation.http.common.contract import Contract


class BookShort(Contract):
    uuid: uuid.UUID
    title: str
    upc: str
    price: Decimal


class CategoryShort(Contract):
    uuid: uuid.UUID
    name: str
