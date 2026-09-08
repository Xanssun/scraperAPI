from typing import Any, Callable

# from src.database.psql import models
from src.database.psql.connection import SessionFactoryType
from src.database.psql.interfaces.gateway import BaseGateway
from src.database.psql.manager import TransactionManager


class DBGateway(BaseGateway):
    __slots__ = ("manager", "_cache")

    def __init__(self, manager: TransactionManager) -> None:
        super().__init__(manager)
        self.manager = manager
        self._cache: dict[str, Any] = {}

    def _from_cache[S](self, key: str, factory: Callable[..., S], **kwargs: Any) -> S:
        if not (cached := self._cache.get(key)):
            cached = factory(self.manager.session, **kwargs)
            self._cache[key] = cached

        return cached


def create_database_factory(
    manager: type[TransactionManager], session_factory: SessionFactoryType
) -> Callable[[], DBGateway]:
    def _create() -> DBGateway:
        return DBGateway(manager(session_factory()))

    return _create


__all__ = ("DBGateway", "create_database_factory")
