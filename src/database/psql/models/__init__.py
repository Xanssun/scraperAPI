from sqla_autoloads import get_node, init_node

from .base import Base
from .book import Book
from .category import Category
from .scrape_run import ScrapeRun

__all__ = ("Base", "Book", "Category", "ScrapeRun")


init_node(get_node(Base))
