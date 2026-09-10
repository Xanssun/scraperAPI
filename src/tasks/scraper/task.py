import asyncio
from dataclasses import dataclass
from datetime import UTC, datetime

import uuid_utils.compat as uuid
from dishka.integrations.taskiq import FromDishka, inject
from taskiq import AsyncBroker

from src.application.v1.results.books_to_scrape import (
    ParsedBookResult,
    ParsedCatalogPageResult,
)
from src.application.v1.services.gateway import ServiceGateway
from src.database.psql import DBGateway
from src.database.psql.models.types import ScrapeRunStatus

SCRAPER_TASK_NAME = "books.scrape"


@dataclass(slots=True)
class ScrapeStats:
    processed_count: int = 0
    created_count: int = 0
    updated_count: int = 0
    error_count: int = 0


async def scrape_books(
    run_uuid: str,
    *,
    start_page: int,
    end_page: int,
    concurrency: int,
    database: FromDishka[DBGateway],
    services: FromDishka[ServiceGateway],
) -> None:
    parsed_run_uuid = uuid.UUID(run_uuid)
    stats = ScrapeStats()

    try:
        books, fetch_errors = await _scrape_books(
            services=services,
            start_page=start_page,
            end_page=end_page,
            concurrency=concurrency,
        )
        stats = await _save_books(database, books, fetch_errors)
        state = (
            ScrapeRunStatus.FAILED if stats.error_count else ScrapeRunStatus.SUCCEEDED
        )
    except Exception:
        stats.error_count += 1
        state = ScrapeRunStatus.FAILED

    await _finish_run(database, parsed_run_uuid, state, stats)


async def _scrape_books(
    *,
    services: ServiceGateway,
    start_page: int,
    end_page: int,
    concurrency: int,
) -> tuple[list[ParsedBookResult], int]:
    semaphore = asyncio.Semaphore(concurrency)
    catalog_results = await asyncio.gather(
        *(
            _scrape_catalog_page(services, page, semaphore)
            for page in range(start_page, end_page + 1)
        ),
        return_exceptions=True,
    )

    catalog_pages: list[ParsedCatalogPageResult] = []
    error_count = 0
    for result in catalog_results:
        if isinstance(result, ParsedCatalogPageResult):
            catalog_pages.append(result)
        else:
            error_count += 1

    book_urls = [
        book.page_url for catalog_page in catalog_pages for book in catalog_page.books
    ]
    book_results = await asyncio.gather(
        *(_scrape_book(services, url, semaphore) for url in book_urls),
        return_exceptions=True,
    )

    books: list[ParsedBookResult] = []
    for book_result in book_results:
        if isinstance(book_result, ParsedBookResult):
            books.append(book_result)
        else:
            error_count += 1

    return books, error_count


async def _scrape_catalog_page(
    services: ServiceGateway,
    page: int,
    semaphore: asyncio.Semaphore,
) -> ParsedCatalogPageResult:
    async with semaphore:
        return await services.books_to_scrape.get_catalog_page(page)


async def _scrape_book(
    services: ServiceGateway,
    url: str,
    semaphore: asyncio.Semaphore,
) -> ParsedBookResult:
    async with semaphore:
        return await services.books_to_scrape.get_book(url)


async def _save_books(
    database: DBGateway,
    books: list[ParsedBookResult],
    fetch_errors: int,
) -> ScrapeStats:
    stats = ScrapeStats(error_count=fetch_errors)

    async with database:
        for book in books:
            category = (
                await database.category.select(name=book.category)
            ).result_or_none()
            if category is None:
                category = (await database.category.create(name=book.category)).result()

            existing_book = (await database.book.select(upc=book.upc)).result_or_none()
            if existing_book is None:
                await database.book.create(
                    title=book.title,
                    upc=book.upc,
                    price=book.price,
                    stock_count=book.stock_count,
                    rating=book.rating,
                    description=book.description,
                    page_url=book.page_url,
                    image_url=book.image_url,
                    category_uuid=category.uuid,
                )
                stats.created_count += 1
            else:
                await database.book.update(
                    existing_book.uuid,
                    title=book.title,
                    price=book.price,
                    stock_count=book.stock_count,
                    rating=book.rating,
                    description=book.description,
                    page_url=book.page_url,
                    image_url=book.image_url,
                    category_uuid=category.uuid,
                )
                stats.updated_count += 1

            stats.processed_count += 1

    return stats


async def _finish_run(
    database: DBGateway,
    run_uuid: uuid.UUID,
    state: ScrapeRunStatus,
    stats: ScrapeStats,
) -> None:
    async with database:
        await database.scrape_run.update(
            run_uuid,
            state=state,
            finished_at=datetime.now(UTC),
            processed_count=stats.processed_count,
            created_count=stats.created_count,
            updated_count=stats.updated_count,
            error_count=stats.error_count,
        )


def setup_scraper_tasks(broker: AsyncBroker) -> None:
    broker.register_task(
        inject(scrape_books, patch_module=True),
        task_name=SCRAPER_TASK_NAME,
    )
