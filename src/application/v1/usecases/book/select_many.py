import uuid
from dataclasses import dataclass
from decimal import Decimal

from src.application.common.interfaces.usecase import UseCase
from src.application.common.pagination import OffsetPagination
from src.application.common.request import Request
from src.application.v1.results import BookResult, OffsetResult
from src.database.psql import DBGateway
from src.database.psql.types.book import BookLoads


class SelectManyBooksRequest(Request):
    loads: tuple[BookLoads, ...] = ()
    category_uuid: uuid.UUID | None = None
    category_name: str | None = None
    price_from: Decimal | None = None
    price_to: Decimal | None = None
    rating: int | None = None
    in_stock: bool | None = None
    pagination: OffsetPagination = OffsetPagination()


@dataclass(slots=True)
class SelectManyBooksUseCase(
    UseCase[SelectManyBooksRequest, OffsetResult[BookResult]]
):
    database: DBGateway

    async def __call__(
        self, request: SelectManyBooksRequest
    ) -> OffsetResult[BookResult]:
        async with self.database.manager.session:
            total, books = (
                await self.database.book.select_many(
                    *request.loads,
                    category_uuid=request.category_uuid,
                    category_name=request.category_name,
                    price_from=request.price_from,
                    price_to=request.price_to,
                    rating=request.rating,
                    in_stock=request.in_stock,
                    **request.pagination.model_dump(),
                )
            ).result()

            return OffsetResult[BookResult](
                data=[BookResult(**book.as_dict()) for book in books],
                offset=request.pagination.offset,
                limit=request.pagination.limit,
                total=total,
            )
