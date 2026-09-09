from typing import Annotated

import uuid_utils.compat as uuid
from dishka.integrations.fastapi import DishkaRoute
from fastapi import APIRouter, Query, status
from fastapi import Depends as Require

from src.application.common.interfaces.request_bus import RequestBus
from src.application.common.pagination import OffsetPagination
from src.application.v1.results import OffsetResult as ApplicationOffsetResult
from src.application.v1.results.book import BookResult
from src.application.v1.usecases.book.select import SelectBookRequest
from src.application.v1.usecases.book.select_many import SelectManyBooksRequest
from src.common.di import Depends
from src.database.psql.types.book import BookLoads
from src.presentation.http.v1 import contracts

book_router = APIRouter(prefix="/books", tags=["Book"], route_class=DishkaRoute)


@book_router.get(
    "",
    response_model=contracts.OffsetResult[contracts.Book],
    status_code=status.HTTP_200_OK,
)
async def select_books_endpoint(
    request_bus: Depends[RequestBus],
    query: Annotated[contracts.SelectBooks, Require(contracts.SelectBooks)],
    pagination: Annotated[
        contracts.OffsetPagination, Require(contracts.OffsetPagination)
    ],
    loads: tuple[BookLoads, ...] = Query(default=(), title="Additional relations"),
) -> contracts.OffsetResult[contracts.Book]:
    result: ApplicationOffsetResult[BookResult] = await request_bus.send(
        SelectManyBooksRequest(
            loads=loads,
            **query.model_dump(),
            pagination=OffsetPagination(**pagination.model_dump()),
        )
    )
    mapped_result = result.map(contracts.Book.model_validate)
    return contracts.OffsetResult[contracts.Book].model_validate(mapped_result)


@book_router.get(
    "/{book_uuid}",
    response_model=contracts.Book,
    status_code=status.HTTP_200_OK,
)
async def select_book_endpoint(
    book_uuid: uuid.UUID,
    request_bus: Depends[RequestBus],
    loads: tuple[BookLoads, ...] = Query(default=(), title="Additional relations"),
) -> contracts.Book:
    result: BookResult = await request_bus.send(
        SelectBookRequest(book_uuid=book_uuid, loads=loads)
    )
    return contracts.Book.model_validate(result)
