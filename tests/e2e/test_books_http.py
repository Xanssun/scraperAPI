from decimal import Decimal

import httpx

from src.database.psql import DBGateway


async def test_get_books_with_rating_filter(
    client: httpx.AsyncClient,
    database: DBGateway,
) -> None:
    async with database:
        category = (await database.category.create(name="Poetry")).result()
        await database.book.create(
            title="Five star book",
            upc="upc-five-star",
            price=Decimal("15.00"),
            stock_count=2,
            rating=5,
            description="Visible through rating filter",
            page_url="https://books.toscrape.com/catalogue/five-star/index.html",
            image_url="https://books.toscrape.com/media/five-star.jpg",
            category_uuid=category.uuid,
        )
        await database.book.create(
            title="Three star book",
            upc="upc-three-star",
            price=Decimal("9.00"),
            stock_count=1,
            rating=3,
            description="Hidden by rating filter",
            page_url="https://books.toscrape.com/catalogue/three-star/index.html",
            image_url="https://books.toscrape.com/media/three-star.jpg",
            category_uuid=category.uuid,
        )

    response = await client.get("/v1/books", params={"rating": 5, "limit": 10})

    assert response.status_code == 200, response.text
    payload = response.json()
    assert payload["total"] == 1
    assert payload["data"][0]["title"] == "Five star book"
    assert payload["data"][0]["rating"] == 5
