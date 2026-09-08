from collections.abc import Sequence
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
from src.database.psql.types.category import (
    CategoryLoads,
    CreateCategoryType,
    UpdateCategoryType,
)


class CategoryRepository(BaseRepository[models.Category]):
    __slots__ = ()

    async def create(self, **data: Unpack[CreateCategoryType]) -> Result[models.Category]:
        return Result("create", await self._crud.insert(**data))

    async def select(
        self,
        *loads: CategoryLoads,
        category_uuid: uuid.UUID | None = None,
        name: str | None = None,
    ) -> Result[models.Category]:
        if not any([category_uuid, name]):
            raise InvalidParamsError("at least one identifier must be provided")

        where_clauses: list[ColumnExpressionArgument[bool]] = []

        if category_uuid:
            where_clauses.append(self.model.uuid == category_uuid)
        if name:
            where_clauses.append(self.model.name == name)

        stmt = sqla_select(model=self.model, loads=loads).where(*where_clauses)
        return Result(
            "select", unique_scalars(await self._session.execute(stmt)).first()
        )

    async def update(
        self,
        uuid: uuid.UUID,
        /,
        **data: Unpack[UpdateCategoryType],
    ) -> Result[models.Category]:
        if not any([uuid]):
            raise InvalidParamsError("at least one identifier must be provided")

        result = await self._crud.update(self.model.uuid == uuid, **data)
        return Result("update", result[0] if result else None)

    async def delete(
        self, category_uuid: uuid.UUID | None = None, name: str | None = None
    ) -> Result[models.Category]:
        if not any([category_uuid, name]):
            raise InvalidParamsError("at least one identifier must be provided")

        where_clauses: list[ColumnExpressionArgument[bool]] = []

        if category_uuid:
            where_clauses.append(self.model.uuid == category_uuid)
        if name:
            where_clauses.append(self.model.name == name)

        result = await self._crud.delete(*where_clauses)
        return Result("delete", result[0] if result else None)

    async def select_many(
        self,
        *loads: CategoryLoads,
        name: str | None = None,
        order_by: OrderBy = "desc",
        offset: int = 0,
        limit: int | None = None,
    ) -> Result[tuple[int, Sequence[models.Category]]]:
        where_clauses: list[ColumnExpressionArgument[bool]] = []

        if name:
            where_clauses.append(self.model.name.ilike(f"%{name}%"))

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
