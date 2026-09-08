from datetime import datetime

import sqlalchemy as sa
import sqlalchemy.orm as orm

from src.common.tools.text import pascal_to_snake
from src.database.psql.models import Base, types
from src.database.psql.models.base import mixins


class ScrapeRun(mixins.UUIDMixin, Base):
    started_at: orm.Mapped[datetime] = orm.mapped_column(
        sa.DateTime(timezone=True),
        nullable=False,
        server_default=sa.func.now(),
    )
    finished_at: orm.Mapped[datetime | None] = orm.mapped_column(
        sa.DateTime(timezone=True),
        nullable=True,
    )
    state: orm.Mapped[types.ScrapeRunStatus] = orm.mapped_column(
        sa.Enum(
            types.ScrapeRunStatus,
            native_enum=False,
            values_callable=lambda x: [e.value for e in x],
            name=pascal_to_snake(types.ScrapeRunStatus),
        ),
        index=True,
        nullable=False,
    )
    processed_count: orm.Mapped[int] = orm.mapped_column(
        sa.Integer,
        nullable=False,
        default=0,
        server_default="0",
    )
    created_count: orm.Mapped[int] = orm.mapped_column(
        sa.Integer,
        nullable=False,
        default=0,
        server_default="0",
    )
    updated_count: orm.Mapped[int] = orm.mapped_column(
        sa.Integer,
        nullable=False,
        default=0,
        server_default="0",
    )
    error_count: orm.Mapped[int] = orm.mapped_column(
        sa.Integer,
        nullable=False,
        default=0,
        server_default="0",
    )
