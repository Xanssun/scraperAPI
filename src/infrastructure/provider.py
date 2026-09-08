from collections.abc import AsyncIterator

from dishka import Provider, Scope, provide

from src.infrastructure.http.provider.aiohttp import AiohttpProvider


class InfrastructureProvider(Provider):
    scope = Scope.APP

    @provide
    async def aiohttp_provider(self) -> AsyncIterator[AiohttpProvider]:
        provider = AiohttpProvider()
        try:
            yield provider
        finally:
            await provider.close_session()
