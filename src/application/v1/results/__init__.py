from .base import OffsetResult, Result, StatusResult
from .book import BookResult, BookShortResult
from .books_to_scrape import (
    ParsedBookPreviewResult,
    ParsedBookResult,
    ParsedCatalogPageResult,
)
from .category import CategoryResult, CategoryShortResult

BookResult.model_rebuild(
    _types_namespace={
        "CategoryShortResult": CategoryShortResult,
    }
)
CategoryResult.model_rebuild(
    _types_namespace={
        "BookShortResult": BookShortResult,
    }
)

__all__ = (
    "BookResult",
    "BookShortResult",
    "CategoryResult",
    "CategoryShortResult",
    "OffsetResult",
    "ParsedBookPreviewResult",
    "ParsedBookResult",
    "ParsedCatalogPageResult",
    "Result",
    "StatusResult",
)
