from decimal import Decimal

from src.application.v1.results.base import Result


class ParsedBookPreviewResult(Result):
    title: str
    page_url: str
    image_url: str
    price: Decimal
    stock_count: int
    rating: int


class ParsedCatalogPageResult(Result):
    page: int
    url: str
    books: list[ParsedBookPreviewResult]
    next_page_url: str | None = None


class ParsedBookResult(ParsedBookPreviewResult):
    upc: str
    category: str
    description: str
