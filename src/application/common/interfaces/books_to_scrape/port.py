from typing import Protocol

from src.application.common.interfaces.books_to_scrape.responses import (
    BookPageResponse,
    CatalogPageResponse,
)


class BooksToScrapeClient(Protocol):
    async def get_catalog_page(self, page: int) -> CatalogPageResponse: ...

    async def get_book_page(self, url_or_path: str) -> BookPageResponse: ...
