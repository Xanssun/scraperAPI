from __future__ import annotations

from collections.abc import AsyncIterator

import httpx
import pytest
from dishka import Provider, Scope, make_async_container, provide
from dishka.integrations.fastapi import FastapiProvider, setup_dishka
from fastapi import FastAPI
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from src.application.common.interfaces.books_to_scrape import BooksToScrapeClient
from src.application.common.interfaces.scrape_tasks import ScrapeTaskProducer
from src.application.provider import ApplicationProvider
from src.database.psql import DBGateway, create_database_factory
from src.database.psql.connection import SessionFactoryType
from src.database.psql.manager import TransactionManager
from src.database.psql.provider import DatabaseFactory
from src.infrastructure.provider import InfrastructureProvider
from src.presentation.http.common.middlewares import setup_global_middlewares
from src.presentation.http.common.responses import ORJSONResponse
from src.presentation.http.v1.endpoints import setup_v1_routers
from src.settings.core import Settings
from src.settings.provider import SettingsProvider
from tests.fakes import FakeBooksToScrapeClient, FakeScrapeTaskProducer


def pytest_collection_modifyitems(
    config: pytest.Config,
    items: list[pytest.Item],
) -> None:
    for item in items:
        if "tests/e2e" in str(item.fspath):
            item.add_marker(pytest.mark.e2e)


class _TestDatabaseProvider(Provider):
    scope = Scope.APP

    def __init__(self, test_factory: async_sessionmaker[AsyncSession]) -> None:
        super().__init__()
        self._test_factory = test_factory

    @provide
    def session_factory(self) -> SessionFactoryType:
        return self._test_factory

    @provide
    def database_factory(self, session_factory: SessionFactoryType) -> DatabaseFactory:
        return create_database_factory(TransactionManager, session_factory)

    @provide(scope=Scope.REQUEST)
    def db_gateway(self, database_factory: DatabaseFactory) -> DBGateway:
        return database_factory()


class _TestExternalProvider(Provider):
    scope = Scope.APP

    @provide
    def books_to_scrape_client(self) -> BooksToScrapeClient:
        return FakeBooksToScrapeClient()

    @provide
    def scrape_task_producer(self) -> ScrapeTaskProducer:
        return FakeScrapeTaskProducer()


@pytest.fixture
async def e2e_app(
    settings: Settings,
    test_session_factory: async_sessionmaker[AsyncSession],
) -> AsyncIterator[FastAPI]:
    container = make_async_container(
        SettingsProvider(),
        InfrastructureProvider(),
        _TestDatabaseProvider(test_session_factory),
        _TestExternalProvider(),
        ApplicationProvider(),
        FastapiProvider(),
        context={Settings: settings},
    )

    app = FastAPI(default_response_class=ORJSONResponse)
    setup_dishka(container, app)
    setup_v1_routers(app)
    setup_global_middlewares(app, settings.server)

    try:
        yield app
    finally:
        await container.close()


@pytest.fixture
async def client(e2e_app: FastAPI) -> AsyncIterator[httpx.AsyncClient]:
    transport = httpx.ASGITransport(app=e2e_app)
    async with httpx.AsyncClient(
        transport=transport,
        base_url="http://testserver",
    ) as test_client:
        yield test_client
