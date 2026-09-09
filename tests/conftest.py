from __future__ import annotations

import os
from collections.abc import AsyncIterator, Iterator

import alembic.command
import psycopg2  # type: ignore[import-untyped]
import pytest
from alembic.config import Config as AlembicConfig
from psycopg2.extensions import (  # type: ignore[import-untyped]
    ISOLATION_LEVEL_AUTOCOMMIT,
)
from sqlalchemy.ext.asyncio import (
    AsyncConnection,
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
)
from testcontainers.postgres import PostgresContainer  # type: ignore[import-untyped]

from src.database.psql import DBGateway
from src.database.psql.connection import create_sa_engine
from src.database.psql.manager import TransactionManager
from src.settings.core import DatabaseSettings, Settings, load_settings, path


@pytest.fixture(scope="session")
def worker_id(request: pytest.FixtureRequest) -> str:
    workerinput = getattr(request.config, "workerinput", None)
    if workerinput is None:
        return "master"
    return str(workerinput.get("workerid", "master"))


@pytest.fixture(scope="session")
def postgres_container() -> Iterator[PostgresContainer]:
    pg = PostgresContainer("postgres:18-alpine")
    if os.name == "nt":
        pg.get_container_host_ip = lambda: "127.0.0.1"
    with pg:
        yield pg


@pytest.fixture(scope="session")
def _worker_database(
    postgres_container: PostgresContainer,
    worker_id: str,
) -> Iterator[str]:
    db_name = f"test_{worker_id}"
    admin_dsn = (
        f"postgresql://{postgres_container.username}:{postgres_container.password}"
        f"@{postgres_container.get_container_host_ip()}"
        f":{postgres_container.get_exposed_port(postgres_container.port)}"
        f"/{postgres_container.dbname}"
    )

    conn = psycopg2.connect(admin_dsn)
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    try:
        with conn.cursor() as cur:
            cur.execute(f'DROP DATABASE IF EXISTS "{db_name}"')
            cur.execute(f'CREATE DATABASE "{db_name}"')
    finally:
        conn.close()

    yield db_name

    conn = psycopg2.connect(admin_dsn)
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    try:
        with conn.cursor() as cur:
            cur.execute(f'DROP DATABASE IF EXISTS "{db_name}"')
    finally:
        conn.close()


@pytest.fixture(scope="session")
def db_settings(
    postgres_container: PostgresContainer,
    _worker_database: str,
) -> DatabaseSettings:
    return DatabaseSettings(
        uri="postgresql+asyncpg://{}:{}@{}:{}/{}",
        name=_worker_database,
        host=postgres_container.get_container_host_ip(),
        port=int(postgres_container.get_exposed_port(postgres_container.port)),
        user=postgres_container.username,
        password=postgres_container.password,
        connection_pool_size=2,
        connection_max_overflow=4,
        connection_pool_pre_ping=False,
    )


@pytest.fixture(scope="session")
def settings(db_settings: DatabaseSettings) -> Settings:
    return load_settings(db=db_settings)


@pytest.fixture(scope="session")
def alembic_config(db_settings: DatabaseSettings) -> AlembicConfig:
    cfg = AlembicConfig(path("alembic.ini"))
    cfg.set_main_option("sqlalchemy.url", db_settings.url)
    return cfg


@pytest.fixture(scope="session")
def _migrate_database(alembic_config: AlembicConfig) -> None:
    alembic.command.upgrade(alembic_config, "head")


@pytest.fixture(scope="session")
async def db_engine(
    db_settings: DatabaseSettings,
    _migrate_database: None,
) -> AsyncIterator[AsyncEngine]:
    engine = create_sa_engine(
        db_settings.url,
        pool_size=db_settings.connection_pool_size,
        max_overflow=db_settings.connection_max_overflow,
        pool_pre_ping=db_settings.connection_pool_pre_ping,
    )

    yield engine

    await engine.dispose()


@pytest.fixture
async def db_connection(db_engine: AsyncEngine) -> AsyncIterator[AsyncConnection]:
    async with db_engine.connect() as connection:
        outer_tx = await connection.begin()
        try:
            yield connection
        finally:
            if outer_tx.is_active:
                await outer_tx.rollback()


@pytest.fixture
def test_session_factory(
    db_connection: AsyncConnection,
) -> async_sessionmaker[AsyncSession]:
    return async_sessionmaker(
        bind=db_connection,
        expire_on_commit=False,
        join_transaction_mode="create_savepoint",
    )


@pytest.fixture
async def db_session(
    test_session_factory: async_sessionmaker[AsyncSession],
) -> AsyncIterator[AsyncSession]:
    session = test_session_factory()
    try:
        yield session
    finally:
        await session.close()


@pytest.fixture
def database(
    test_session_factory: async_sessionmaker[AsyncSession],
) -> DBGateway:
    return DBGateway(TransactionManager(test_session_factory()))
