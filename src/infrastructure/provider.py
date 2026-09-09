from collections.abc import AsyncIterator

from dishka import Provider, Scope, provide

from src.application.common.interfaces.books_to_scrape import BooksToScrapeClient
from src.infrastructure.http.clients.books_to_scrape import BooksToScrapeAPI
from src.infrastructure.http.provider.aiohttp import AiohttpProvider
from src.settings.core import Settings


class InfrastructureProvider(Provider):
    scope = Scope.APP

    @provide
    async def aiohttp_provider(self) -> AsyncIterator[AiohttpProvider]:
        provider = AiohttpProvider()
        try:
            yield provider
        finally:
            await provider.close_session()

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
