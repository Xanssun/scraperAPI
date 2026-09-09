from dataclasses import dataclass
from datetime import datetime

from pydantic import model_validator

from src.application.common.interfaces.usecase import UseCase
from src.application.common.pagination import OffsetPagination
from src.application.common.request import Request
from src.application.v1.results import OffsetResult
from src.application.v1.results.scrape_run import ScrapeRunResult
from src.database.psql import DBGateway
from src.database.psql.models.types import ScrapeRunStatus


class SelectManyScrapeRunsRequest(Request):
    state: ScrapeRunStatus | None = None
    started_from: datetime | None = None
    started_to: datetime | None = None
    pagination: OffsetPagination = OffsetPagination()

    @model_validator(mode="after")
    def validate_started_range(self) -> "SelectManyScrapeRunsRequest":
        if (
            self.started_from is not None
            and self.started_to is not None
            and self.started_to < self.started_from
        ):
            raise ValueError("started_to must be greater than or equal to started_from")

        return self


@dataclass(slots=True)
class SelectManyScrapeRunsUseCase(
    UseCase[SelectManyScrapeRunsRequest, OffsetResult[ScrapeRunResult]]
):
    database: DBGateway

    async def __call__(
        self, request: SelectManyScrapeRunsRequest
    ) -> OffsetResult[ScrapeRunResult]:
        async with self.database.manager.session:
            total, scrape_runs = (
                await self.database.scrape_run.select_many(
                    state=request.state,
                    started_from=request.started_from,
                    started_to=request.started_to,
                    **request.pagination.model_dump(),
                )
            ).result()

            return OffsetResult[ScrapeRunResult](
                data=[
                    ScrapeRunResult.model_validate(scrape_run)
                    for scrape_run in scrape_runs
                ],
                offset=request.pagination.offset,
                limit=request.pagination.limit,
                total=total,
            )
