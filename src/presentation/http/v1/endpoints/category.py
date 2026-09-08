from typing import Annotated

from dishka.integrations.fastapi import DishkaRoute
from fastapi import APIRouter, Query, status
from fastapi import Depends as Require

from src.application.common.interfaces.request_bus import RequestBus
from src.application.common.pagination import OffsetPagination
from src.application.v1.results import OffsetResult as ApplicationOffsetResult
from src.application.v1.results.category import CategoryResult
from src.application.v1.usecases.category.select_many import SelectManyCategoriesRequest
from src.common.di import Depends
from src.database.psql.types.category import CategoryLoads
from src.presentation.http.v1 import contracts

category_router = APIRouter(
    prefix="/categories",
    tags=["Category"],
    route_class=DishkaRoute,
)


@category_router.get(
    "",
    response_model=contracts.OffsetResult[contracts.Category],
    status_code=status.HTTP_200_OK,
)
async def select_categories_endpoint(
    request_bus: Depends[RequestBus],
    query: Annotated[contracts.SelectCategories, Require(contracts.SelectCategories)],
    pagination: Annotated[
        contracts.OffsetPagination, Require(contracts.OffsetPagination)
    ],
    loads: tuple[CategoryLoads, ...] = Query(default=(), title="Additional relations"),
) -> contracts.OffsetResult[contracts.Category]:
    result: ApplicationOffsetResult[CategoryResult] = await request_bus.send(
        SelectManyCategoriesRequest(
            loads=loads,
            **query.model_dump(),
            pagination=OffsetPagination(**pagination.model_dump()),
        )
    )
    mapped_result = result.map(contracts.Category.model_validate)
    return contracts.OffsetResult[contracts.Category].model_validate(mapped_result)
