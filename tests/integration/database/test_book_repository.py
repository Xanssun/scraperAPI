from decimal import Decimal

from sqlalchemy import func, select

import src.database.psql.models as models
from src.database.psql import DBGateway


async def test_book_create_update_by_existing_upc_does_not_duplicate(
    database: DBGateway,
) -> None:
    async with database:
        category = (await database.category.create(name="Travel")).result()
        created_book = (
            await database.book.create(
                title="Original title",
                upc="upc-1",
                price=Decimal("10.00"),
                stock_count=3,
                rating=4,
                description="Original description",
                page_url="https://books.toscrape.com/catalogue/original/index.html",
                image_url="https://books.toscrape.com/media/original.jpg",
                category_uuid=category.uuid,
            )
        ).result()

        existing_book = (await database.book.select(upc="upc-1")).result()
        updated_book = (
            await database.book.update(
                existing_book.uuid,
                title="Updated title",
                price=Decimal("12.50"),
                stock_count=8,
                rating=5,
                description="Updated description",
                page_url="https://books.toscrape.com/catalogue/original/index.html",
                image_url="https://books.toscrape.com/media/updated.jpg",
                category_uuid=category.uuid,
            )
        ).result()

        total_books = await database.manager.session.scalar(
            select(func.count()).select_from(models.Book).where(models.Book.upc == "upc-1")
        )

    assert created_book.uuid == updated_book.uuid
    assert updated_book.price == Decimal("12.50")
    assert updated_book.stock_count == 8
    assert total_books == 1
