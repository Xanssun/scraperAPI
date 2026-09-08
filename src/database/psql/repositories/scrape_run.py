from collections.abc import Sequence
from datetime import datetime
from typing import Unpack

import uuid_utils.compat as uuid
from sqlalchemy import ColumnExpressionArgument

import src.database.psql.models as models
from src.database.psql.models.types import ScrapeRunStatus
from src.database.psql.repositories import Result
from src.database.psql.repositories.base import BaseRepository
from src.database.psql.tools import sqla_offset_query, unique_scalars
from src.database.psql.types import OrderBy
from src.database.psql.types.scrape_run import (
    CreateScrapeRunType,
    UpdateScrapeRunType,
)


class ScrapeRunRepository(BaseRepository[models.ScrapeRun]):
    __slots__ = ()

    async def create(
        self,
        **data: Unpack[CreateScrapeRunType],
    ) -> Result[models.ScrapeRun]:
        return Result("create", await self._crud.insert(**data))

    async def select(
        self,
        scrape_run_uuid: uuid.UUID,
    ) -> Result[models.ScrapeRun]:
        return Result(
            "select",
            await self._crud.select(self.model.uuid == scrape_run_uuid),
        )

    async def update(
        self,
        scrape_run_uuid: uuid.UUID,
        /,
        **data: Unpack[UpdateScrapeRunType],
    ) -> Result[models.ScrapeRun]:
        result = await self._crud.update(self.model.uuid == scrape_run_uuid, **data)
        return Result("update", result[0] if result else None)

    async def delete(self, scrape_run_uuid: uuid.UUID) -> Result[models.ScrapeRun]:
        result = await self._crud.delete(self.model.uuid == scrape_run_uuid)
        return Result("delete", result[0] if result else None)

    async def select_many(
        self,
        state: ScrapeRunStatus | None = None,
        started_from: datetime | None = None,
        started_to: datetime | None = None,
        order_by: OrderBy = "desc",
        offset: int = 0,
        limit: int | None = None,
    ) -> Result[tuple[int, Sequence[models.ScrapeRun]]]:
        where_clauses: list[ColumnExpressionArgument[bool]] = []

        if state:
            where_clauses.append(self.model.state == state)
        if started_from:
            where_clauses.append(self.model.started_at >= started_from)
        if started_to:
            where_clauses.append(self.model.started_at <= started_to)

        total = await self._crud.count(*where_clauses)
        if total <= 0:
            return Result("select", (total, []))

        stmt = sqla_offset_query(
            self.model,
            offset=offset,
            limit=limit,
            order=("started_at", order_by),
            where=where_clauses,
        )

        results = unique_scalars(await self._session.execute(stmt)).all()
        return Result("select", (total, results))
