from urllib.parse import urljoin

from src.application.common.interfaces.books_to_scrape.responses import (
    BookPageResponse,
    CatalogPageResponse,
)
from src.infrastructure.http.clients.books_to_scrape.endpoints import (
    BooksToScrapeEndpoint,
)
from src.infrastructure.http.provider import AsyncProvider


class BooksToScrapeAPI:
    __slots__ = ("_base_url", "_provider")

    def __init__(
        self,
        provider: AsyncProvider,
        base_url: str,
    ) -> None:
        self._provider = provider
        self._base_url = base_url

    async def get_catalog_page(self, page: int) -> CatalogPageResponse:
        endpoint = (
            BooksToScrapeEndpoint.HOME
            if page == 1
            else BooksToScrapeEndpoint.CATALOG_PAGE.format(page=page)
        )
        url = self._url(endpoint)
        response = await self._provider("GET", url)
        return CatalogPageResponse(
            page=page,
            url=response.url,
            html=await response.text(),
        )

    async def get_book_page(self, url_or_path: str) -> BookPageResponse:
        response = await self._provider("GET", self._url(url_or_path))
        return BookPageResponse(
            url=response.url,
            html=await response.text(),
        )

    def _url(self, url_or_path: str) -> str:
        return urljoin(self._base_url, url_or_path)
