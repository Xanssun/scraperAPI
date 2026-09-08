from collections.abc import Sequence
from decimal import Decimal
from typing import Unpack

import uuid_utils.compat as uuid
from sqlalchemy import ColumnExpressionArgument

import src.database.psql.models as models
from src.database.psql.exceptions import InvalidParamsError
from src.database.psql.repositories import Result
from src.database.psql.repositories.base import BaseRepository
from src.database.psql.tools import (
    sqla_offset_query,
    sqla_select,
    unique_scalars,
)
from src.database.psql.types import OrderBy
from src.database.psql.types.book import (
    BookLoads,
    CreateBookType,
    UpdateBookType,
)


class BookRepository(BaseRepository[models.Book]):
    __slots__ = ()

    async def create(self, **data: Unpack[CreateBookType]) -> Result[models.Book]:
        return Result("create", await self._crud.insert(**data))

    async def select(
        self,
        *loads: BookLoads,
        book_uuid: uuid.UUID | None = None,
        upc: str | None = None,
        page_url: str | None = None,
    ) -> Result[models.Book]:
        if not any([book_uuid, upc, page_url]):
            raise InvalidParamsError("at least one identifier must be provided")

        where_clauses: list[ColumnExpressionArgument[bool]] = []

        if book_uuid:
            where_clauses.append(self.model.uuid == book_uuid)
        if upc:
            where_clauses.append(self.model.upc == upc)
        if page_url:
            where_clauses.append(self.model.page_url == page_url)

        stmt = sqla_select(model=self.model, loads=loads).where(*where_clauses)
        return Result(
            "select",
            unique_scalars(await self._session.execute(stmt)).first(),
        )

    async def update(
        self,
        book_uuid: uuid.UUID,
        /,
        **data: Unpack[UpdateBookType],
    ) -> Result[models.Book]:
        result = await self._crud.update(self.model.uuid == book_uuid, **data)
        return Result("update", result[0] if result else None)

    async def delete(
        self,
        book_uuid: uuid.UUID | None = None,
        upc: str | None = None,
    ) -> Result[models.Book]:
        if not any([book_uuid, upc]):
            raise InvalidParamsError("at least one identifier must be provided")

        where_clauses: list[ColumnExpressionArgument[bool]] = []

        if book_uuid:
            where_clauses.append(self.model.uuid == book_uuid)
        if upc:
            where_clauses.append(self.model.upc == upc)

        result = await self._crud.delete(*where_clauses)
        return Result("delete", result[0] if result else None)

    async def select_many(
        self,
        *loads: BookLoads,
        title: str | None = None,
        category_uuid: uuid.UUID | None = None,
        category_name: str | None = None,
        price_from: Decimal | None = None,
        price_to: Decimal | None = None,
        rating: int | None = None,
        in_stock: bool | None = None,
        order_by: OrderBy = "desc",
        offset: int = 0,
        limit: int | None = None,
    ) -> Result[tuple[int, Sequence[models.Book]]]:
        where_clauses: list[ColumnExpressionArgument[bool]] = []

        if title:
            where_clauses.append(self.model.title.ilike(f"%{title}%"))
        if category_uuid:
            where_clauses.append(self.model.category_uuid == category_uuid)
        if category_name:
            where_clauses.append(
                self.model.category.has(models.Category.name == category_name)
            )
        if price_from is not None:
            where_clauses.append(self.model.price >= price_from)
        if price_to is not None:
            where_clauses.append(self.model.price <= price_to)
        if rating is not None:
            where_clauses.append(self.model.rating == rating)
        if in_stock is not None:
            where_clauses.append(
                self.model.stock_count > 0
                if in_stock
                else self.model.stock_count == 0
            )

        total = await self._crud.count(*where_clauses)
        if total <= 0:
            return Result("select", (total, []))

        stmt = sqla_offset_query(
            self.model,
            loads=loads,
            offset=offset,
            limit=limit,
            order=("created_at", order_by),
            where=where_clauses,
        )

        results = unique_scalars(await self._session.execute(stmt)).all()
        return Result("select", (total, results))
