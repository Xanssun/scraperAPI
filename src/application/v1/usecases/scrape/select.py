from dataclasses import dataclass

import uuid_utils.compat as uuid

from src.application.common.interfaces.usecase import UseCase
from src.application.common.request import Request
from src.application.v1.results.scrape_run import ScrapeRunResult
from src.database.psql import DBGateway


class SelectScrapeRunRequest(Request):
    scrape_run_uuid: uuid.UUID


@dataclass(slots=True)
class SelectScrapeRunUseCase(UseCase[SelectScrapeRunRequest, ScrapeRunResult]):
    database: DBGateway

    async def __call__(self, request: SelectScrapeRunRequest) -> ScrapeRunResult:
        async with self.database.manager.session:
            scrape_run = (
                await self.database.scrape_run.select(request.scrape_run_uuid)
            ).result()
            return ScrapeRunResult.model_validate(scrape_run)
