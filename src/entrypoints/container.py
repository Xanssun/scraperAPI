from dishka import AsyncContainer, Provider, make_async_container

from src.application.provider import ApplicationProvider
from src.database.psql.provider import DatabaseProvider
from src.infrastructure.http.clients.provider import HttpClientsProvider
from src.infrastructure.provider import InfrastructureProvider
from src.settings.core import Settings
from src.settings.provider import SettingsProvider
from src.tasks.provider import TasksProvider


def build_container(settings: Settings, *extra: Provider) -> AsyncContainer:
    return make_async_container(
        SettingsProvider(),
        InfrastructureProvider(),
        HttpClientsProvider(),
        TasksProvider(),
        DatabaseProvider(),
        ApplicationProvider(),
        *extra,
        context={Settings: settings},
    )
