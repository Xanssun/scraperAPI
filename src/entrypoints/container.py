from dishka import AsyncContainer, Provider, make_async_container

from src.settings.core import Settings
from src.settings.provider import SettingsProvider


def build_container(settings: Settings, *extra: Provider) -> AsyncContainer:
    return make_async_container(
        SettingsProvider(),
        *extra,
        context={Settings: settings},
    )
