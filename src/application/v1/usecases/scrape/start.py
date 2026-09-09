from dataclasses import dataclass
from datetime import UTC, datetime

from pydantic import Field, model_validator

from src.application.common.interfaces.scrape_tasks import ScrapeTaskProducer
from src.application.common.interfaces.usecase import UseCase
from src.application.common.request import Request
from src.application.v1.results.scrape_run import ScrapeRunResult
from src.database.psql import DBGateway
from src.database.psql.models.types import ScrapeRunStatus


class StartBooksScrapeRequest(Request):
    start_page: int = Field(default=1, ge=1)
    end_page: int = Field(default=50, ge=1)
    concurrency: int = Field(default=10, ge=1, le=10)

    @model_validator(mode="after")
    def validate_pages_range(self) -> "StartBooksScrapeRequest":
        if self.end_page < self.start_page:
            raise ValueError("end_page must be greater than or equal to start_page")

        return self


@dataclass(slots=True)
class StartBooksScrapeUseCase(UseCase[StartBooksScrapeRequest, ScrapeRunResult]):
    database: DBGateway
    scrape_tasks: ScrapeTaskProducer

    async def __call__(self, request: StartBooksScrapeRequest) -> ScrapeRunResult:
        async with self.database:
            run = (
                await self.database.scrape_run.create(
                    state=ScrapeRunStatus.RUNNING,
                )
            ).result()

        try:
            await self.scrape_tasks.enqueue_books_scrape(
                run.uuid,
                start_page=request.start_page,
                end_page=request.end_page,
                concurrency=request.concurrency,
            )
        except Exception:
            async with self.database:
                run = (
                    await self.database.scrape_run.update(
                        run.uuid,
                        state=ScrapeRunStatus.FAILED,
                        finished_at=datetime.now(UTC),
                        error_count=1,
                    )
                ).result()

        return ScrapeRunResult.model_validate(run)
