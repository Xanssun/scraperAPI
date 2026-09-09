from dishka import Provider, Scope, provide

from src.application.common.interfaces.books_to_scrape import BooksToScrapeClient
from src.infrastructure.http.clients.books_to_scrape import BooksToScrapeAPI
from src.infrastructure.http.provider.aiohttp import AiohttpProvider
from src.settings.core import Settings


class HttpClientsProvider(Provider):
    scope = Scope.APP

    @provide
    def books_to_scrape_client(
        self,
        provider: AiohttpProvider,
        settings: Settings,
    ) -> BooksToScrapeClient:
        return BooksToScrapeAPI(
            provider=provider,
            base_url=settings.books_to_scrape.base_url,
        )
