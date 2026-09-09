from typing import Callable

from dishka import Provider, Scope, provide

from src.application.common.bus import RequestBusImpl
from src.application.common.interfaces.books_to_scrape import BooksToScrapeClient
from src.application.common.interfaces.request_bus import RequestBus
from src.application.common.interfaces.scrape_tasks import ScrapeTaskProducer
from src.application.v1.services import BooksToScrapeService
from src.application.v1.services.gateway import ServiceGateway
from src.application.v1.usecases import setup_use_cases
from src.database.psql import DBGateway

type DatabaseFactory = Callable[[], DBGateway]


class ApplicationProvider(Provider):
    scope = Scope.APP

    @provide
    def books_to_scrape_service(
        self,
        client: BooksToScrapeClient,
    ) -> BooksToScrapeService:
        return BooksToScrapeService(client=client)

    @provide
    def service_gateway(self, books_to_scrape: BooksToScrapeService) -> ServiceGateway:
        return ServiceGateway(books_to_scrape=books_to_scrape)

    @provide
    def request_bus(
        self,
        database_factory: DatabaseFactory,
        services: ServiceGateway,
        scrape_tasks: ScrapeTaskProducer,
    ) -> RequestBus:
        return (
            RequestBusImpl.builder()
            .dependencies(
                database=database_factory,
                services=services,
                scrape_tasks=scrape_tasks,
            )
            .use_cases(setup_use_cases)
            .build()
        )
