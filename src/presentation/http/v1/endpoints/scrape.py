from typing import Annotated

import uuid_utils.compat as uuid
from dishka.integrations.fastapi import DishkaRoute
from fastapi import APIRouter, status
from fastapi import Depends as Require

from src.application.common.interfaces.request_bus import RequestBus
from src.application.common.pagination import OffsetPagination
from src.application.v1.results import OffsetResult as ApplicationOffsetResult
from src.application.v1.results.scrape_run import ScrapeRunResult
from src.application.v1.usecases.scrape.select import SelectScrapeRunRequest
from src.application.v1.usecases.scrape.select_many import SelectManyScrapeRunsRequest
from src.application.v1.usecases.scrape.start import StartBooksScrapeRequest
from src.common.di import Depends
from src.presentation.http.v1 import contracts

scrape_router = APIRouter(prefix="/scrape", tags=["Scrape"], route_class=DishkaRoute)


@scrape_router.post(
    "",
    response_model=contracts.ScrapeRun,
    status_code=status.HTTP_202_ACCEPTED,
)
async def start_books_scrape_endpoint(
    request_bus: Depends[RequestBus],
    body: contracts.StartBooksScrape,
) -> contracts.ScrapeRun:
    result: ScrapeRunResult = await request_bus.send(
        StartBooksScrapeRequest(**body.model_dump())
    )
    return contracts.ScrapeRun.model_validate(result)


@scrape_router.get(
    "/runs",
    response_model=contracts.OffsetResult[contracts.ScrapeRun],
    status_code=status.HTTP_200_OK,
)
async def select_scrape_runs_endpoint(
    request_bus: Depends[RequestBus],
    query: Annotated[contracts.SelectScrapeRuns, Require(contracts.SelectScrapeRuns)],
    pagination: Annotated[
        contracts.OffsetPagination, Require(contracts.OffsetPagination)
    ],
) -> contracts.OffsetResult[contracts.ScrapeRun]:
    result: ApplicationOffsetResult[ScrapeRunResult] = await request_bus.send(
        SelectManyScrapeRunsRequest(
            **query.model_dump(),
            pagination=OffsetPagination(**pagination.model_dump()),
        )
    )
    mapped_result = result.map(contracts.ScrapeRun.model_validate)
    return contracts.OffsetResult[contracts.ScrapeRun].model_validate(mapped_result)


@scrape_router.get(
    "/runs/{scrape_run_uuid}",
    response_model=contracts.ScrapeRun,
    status_code=status.HTTP_200_OK,
)
async def select_scrape_run_endpoint(
    scrape_run_uuid: uuid.UUID,
    request_bus: Depends[RequestBus],
) -> contracts.ScrapeRun:
    result: ScrapeRunResult = await request_bus.send(
        SelectScrapeRunRequest(scrape_run_uuid=scrape_run_uuid)
    )
    return contracts.ScrapeRun.model_validate(result)
