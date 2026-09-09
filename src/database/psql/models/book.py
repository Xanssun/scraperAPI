from decimal import Decimal
from typing import TYPE_CHECKING

import sqlalchemy as sa
import sqlalchemy.orm as orm
from sqlalchemy.dialects.postgresql import UUID
from uuid_utils.compat import UUID as uuid_type

from src.database.psql.models.base import Base, mixins

if TYPE_CHECKING:
    from src.database.psql.models import Category


class Book(mixins.UUIDMixin, mixins.TimeMixin, Base):
    title: orm.Mapped[str] = orm.mapped_column(
        sa.String,
        index=True,
        nullable=False,
    )
    upc: orm.Mapped[str] = orm.mapped_column(
        sa.String(64),
        unique=True,
        index=True,
        nullable=False,
    )
    price: orm.Mapped[Decimal] = orm.mapped_column(
        sa.Numeric(10, 2),
        nullable=False,
    )
    stock_count: orm.Mapped[int] = orm.mapped_column(
        sa.Integer,
        nullable=False,
    )
    rating: orm.Mapped[int] = orm.mapped_column(
        sa.SmallInteger,
        nullable=False,
    )
    description: orm.Mapped[str] = orm.mapped_column(
        sa.Text,
        nullable=False,
    )
    page_url: orm.Mapped[str] = orm.mapped_column(
        sa.String,
        unique=True,
        nullable=False,
    )
    image_url: orm.Mapped[str] = orm.mapped_column(
        sa.String,
        nullable=False,
    )
    category_uuid: orm.Mapped[uuid_type] = orm.mapped_column(
        UUID(as_uuid=True),
        sa.ForeignKey("category.uuid", ondelete="RESTRICT"),
        index=True,
        nullable=False,
    )

    category: orm.Mapped["Category"] = orm.relationship(
        back_populates="books",
    )
