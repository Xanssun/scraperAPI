from src.application.v1.services.books_to_scrape import BooksToScrapeService


class ServiceGateway:
    __slots__ = ("_books_to_scrape",)

    def __init__(self, books_to_scrape: BooksToScrapeService) -> None:
        self._books_to_scrape = books_to_scrape

    @property
    def books_to_scrape(self) -> BooksToScrapeService:
        return self._books_to_scrape
