from dataclasses import dataclass

from src.application.common.interfaces.usecase import UseCase
from src.application.common.pagination import OffsetPagination
from src.application.common.request import Request
from src.application.v1.results import CategoryResult, OffsetResult
from src.database.psql import DBGateway
from src.database.psql.types.category import CategoryLoads


class SelectManyCategoriesRequest(Request):
    loads: tuple[CategoryLoads, ...] = ()
    name: str | None = None
    pagination: OffsetPagination = OffsetPagination()


@dataclass(slots=True)
class SelectManyCategoriesUseCase(
    UseCase[SelectManyCategoriesRequest, OffsetResult[CategoryResult]]
):
    database: DBGateway

    async def __call__(
        self, request: SelectManyCategoriesRequest
    ) -> OffsetResult[CategoryResult]:
        async with self.database.manager.session:
            total, categories = (
                await self.database.category.select_many(
                    *request.loads,
                    name=request.name,
                    **request.pagination.model_dump(),
                )
            ).result()

            return OffsetResult[CategoryResult](
                data=[CategoryResult(**category.as_dict()) for category in categories],
                offset=request.pagination.offset,
                limit=request.pagination.limit,
                total=total,
            )
