from typing import Callable

from dishka import Provider, Scope, provide

from src.application.common.bus import RequestBusImpl
from src.application.common.interfaces.request_bus import RequestBus
from src.application.v1.usecases import setup_use_cases
from src.database.psql import DBGateway

type DatabaseFactory = Callable[[], DBGateway]


class ApplicationProvider(Provider):
    scope = Scope.APP

    @provide
    def request_bus(
        self,
        database_factory: DatabaseFactory,
    ) -> RequestBus:
        return (
            RequestBusImpl.builder()
            .dependencies(
                database=database_factory,
            )
            .use_cases(setup_use_cases)
            .build()
        )
