from __future__ import annotations

from dataclasses import dataclass, field

import uuid_utils.compat as uuid

from src.application.common.interfaces.books_to_scrape.responses import (
    BookPageResponse,
    CatalogPageResponse,
)


@dataclass(slots=True)
class EnqueuedBooksScrape:
    run_uuid: uuid.UUID
    start_page: int
    end_page: int
    concurrency: int


@dataclass(slots=True)
class FakeScrapeTaskProducer:
    enqueued: list[EnqueuedBooksScrape] = field(default_factory=list)

    async def enqueue_books_scrape(
        self,
        run_uuid: uuid.UUID,
        *,
        start_page: int,
        end_page: int,
        concurrency: int,
    ) -> None:
        self.enqueued.append(
            EnqueuedBooksScrape(
                run_uuid=run_uuid,
                start_page=start_page,
                end_page=end_page,
                concurrency=concurrency,
            )
        )


@dataclass(slots=True)
class FakeBooksToScrapeClient:
    catalog_pages: dict[int, CatalogPageResponse] = field(default_factory=dict)
    book_pages: dict[str, BookPageResponse] = field(default_factory=dict)

    async def get_catalog_page(self, page: int) -> CatalogPageResponse:
        try:
            return self.catalog_pages[page]
        except KeyError as e:
            raise ValueError(f"Catalog page fixture `{page}` is not registered") from e

    async def get_book_page(self, url_or_path: str) -> BookPageResponse:
        try:
            return self.book_pages[url_or_path]
        except KeyError as e:
            raise ValueError(
                f"Book page fixture `{url_or_path}` is not registered"
            ) from e
