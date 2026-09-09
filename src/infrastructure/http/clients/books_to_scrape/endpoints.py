from enum import StrEnum


class BooksToScrapeEndpoint(StrEnum):
    HOME = ""
    CATALOG_PAGE = "catalogue/page-{page}.html"
