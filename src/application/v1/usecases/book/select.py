from dataclasses import dataclass

import uuid_utils.compat as uuid

from src.application.common.interfaces.usecase import UseCase
from src.application.common.request import Request
from src.application.v1.results import BookResult
from src.database.psql import DBGateway
from src.database.psql.types.book import BookLoads


class SelectBookRequest(Request):
    loads: tuple[BookLoads, ...] = ()
    book_uuid: uuid.UUID | None = None
    upc: str | None = None
    page_url: str | None = None


@dataclass(slots=True)
class SelectBookUseCase(UseCase[SelectBookRequest, BookResult]):
    database: DBGateway

    async def __call__(self, request: SelectBookRequest) -> BookResult:
        async with self.database.manager.session:
            book = (
                await self.database.book.select(
                    *request.loads,
                    book_uuid=request.book_uuid,
                    upc=request.upc,
                    page_url=request.page_url,
                )
            ).result()
            return BookResult(**book.as_dict())
