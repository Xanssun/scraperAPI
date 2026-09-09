from src.presentation.http.common.contract import Contract

from .book import Book, SelectBooks
from .category import Category, SelectCategories
from .pagination import OffsetPagination
from .scrape import ScrapeRun, SelectScrapeRuns, StartBooksScrape
from .short import BookShort, CategoryShort

__all__ = (
    "Contract",
    "OffsetPagination",
    "Category",
    "CategoryShort",
    "SelectCategories",
    "Book",
    "BookShort",
    "SelectBooks",
    "ScrapeRun",
    "SelectScrapeRuns",
    "StartBooksScrape",
)


class OffsetResult[T](Contract):
    data: list[T]
    offset: int = 0
    limit: int | None = None
    total: int
