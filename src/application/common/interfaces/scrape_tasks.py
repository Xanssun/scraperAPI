from typing import Protocol

import uuid_utils.compat as uuid


class ScrapeTaskProducer(Protocol):
    async def enqueue_books_scrape(
        self,
        run_uuid: uuid.UUID,
        *,
        start_page: int,
        end_page: int,
        concurrency: int,
    ) -> None: ...
