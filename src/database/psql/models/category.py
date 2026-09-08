from typing import TYPE_CHECKING

import sqlalchemy as sa
import sqlalchemy.orm as orm

from src.database.psql.models.base import Base, mixins

if TYPE_CHECKING:
    from src.database.psql.models import Book


class Category(mixins.UUIDMixin, mixins.TimeMixin, Base):
    name: orm.Mapped[str] = orm.mapped_column(
        sa.String,
        unique=True,
        index=True,
        nullable=False,
    )

    books: orm.Mapped[list["Book"]] = orm.relationship(
        back_populates="category",
        passive_deletes=True,
    )
