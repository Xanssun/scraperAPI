from decimal import Decimal
from pathlib import Path

from src.application.common.interfaces.books_to_scrape.responses import BookPageResponse
from src.application.v1.services.books_to_scrape import BooksToScrapeService
from tests.fakes import FakeBooksToScrapeClient


async def test_parse_book_page_from_html_fixture() -> None:
    url = "https://books.toscrape.com/catalogue/a-light-in-the-attic_1000/index.html"
    html = Path("tests/fixtures/book_page.html").read_text(encoding="utf-8")
    client = FakeBooksToScrapeClient(
        book_pages={
            url: BookPageResponse(
                url=url,
                html=html,
            )
        }
    )
    service = BooksToScrapeService(client=client)

    book = await service.get_book(url)

    assert book.title == "A Light in the Attic"
    assert book.upc == "a897fe39b1053632"
    assert book.price == Decimal("51.77")
    assert book.stock_count == 22
    assert book.rating == 3
    assert book.category == "Mystery"
    assert (
        book.description == "It's hard to imagine a world without A Light in the Attic."
    )
    assert book.page_url == url
    assert book.image_url == (
        "https://books.toscrape.com/media/cache/fe/72/"
        "fe72f0532301ec28892ae79a629a293c.jpg"
    )
