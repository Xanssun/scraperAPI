from decimal import Decimal
from re import search
from typing import cast
from urllib.parse import urljoin

from bs4 import BeautifulSoup, Tag
from bs4.element import PageElement

from src.application.common.interfaces.books_to_scrape import BooksToScrapeClient
from src.application.v1.results.books_to_scrape import (
    ParsedBookPreviewResult,
    ParsedBookResult,
    ParsedCatalogPageResult,
)
from src.application.v1.services.types import RATING_MAP


class BooksToScrapeService:
    __slots__ = ("_client",)

    def __init__(self, client: BooksToScrapeClient) -> None:
        self._client = client

    async def get_catalog_page(self, page: int) -> ParsedCatalogPageResult:
        response = await self._client.get_catalog_page(page)
        soup = BeautifulSoup(response.html, "html.parser")

        return ParsedCatalogPageResult(
            page=response.page,
            url=response.url,
            books=[
                self._parse_book_preview(node, response.url)
                for node in soup.select(".product_pod")
            ],
            next_page_url=self._parse_next_page_url(soup, response.url),
        )

    async def get_book(self, url_or_path: str) -> ParsedBookResult:
        response = await self._client.get_book_page(url_or_path)
        soup = BeautifulSoup(response.html, "html.parser")

        product_info = self._parse_product_info(soup)
        title = self._text_required(soup.select_one(".product_main h1"), "book title")
        price = self._parse_price(
            product_info.get("Price (incl. tax)")
            or product_info.get("Price (excl. tax)")
            or self._text_required(soup.select_one(".price_color"), "book price")
        )

        return ParsedBookResult(
            title=title,
            upc=self._required(product_info.get("UPC"), "book upc"),
            price=price,
            stock_count=self._parse_stock_count(
                product_info.get("Availability")
                or self._text_required(
                    soup.select_one(".availability"),
                    "book availability",
                )
            ),
            rating=self._parse_rating(soup.select_one(".star-rating")),
            category=self._parse_category(soup),
            description=self._parse_description(soup),
            page_url=response.url,
            image_url=self._parse_image_url(soup, response.url),
        )

    def _parse_book_preview(
        self,
        node: Tag,
        page_url: str,
    ) -> ParsedBookPreviewResult:
        title_node = node.select_one("h3 a")
        image_node = node.select_one(".image_container img")

        return ParsedBookPreviewResult(
            title=self._attr_required(title_node, "title", "book title"),
            page_url=urljoin(
                page_url,
                self._attr_required(title_node, "href", "book url"),
            ),
            image_url=urljoin(
                page_url,
                self._attr_required(image_node, "src", "book image"),
            ),
            price=self._parse_price(
                self._text_required(node.select_one(".price_color"), "book price")
            ),
            stock_count=self._parse_stock_count(
                self._text_required(node.select_one(".availability"), "book availability")
            ),
            rating=self._parse_rating(node.select_one(".star-rating")),
        )

    def _parse_product_info(self, soup: BeautifulSoup) -> dict[str, str]:
        result: dict[str, str] = {}
        for row in soup.select("table.table-striped tr"):
            header = row.select_one("th")
            value = row.select_one("td")
            if header and value:
                result[header.get_text(strip=True)] = value.get_text(strip=True)

        return result

    def _parse_next_page_url(
        self,
        soup: BeautifulSoup,
        page_url: str,
    ) -> str | None:
        next_page = soup.select_one(".pager .next a")
        if not next_page:
            return None

        href = self._attr_optional(next_page, "href")
        return urljoin(page_url, href) if href else None

    def _parse_category(self, soup: BeautifulSoup) -> str:
        category = soup.select("ul.breadcrumb li a")[-1]
        return category.get_text(strip=True)

    def _parse_description(self, soup: BeautifulSoup) -> str:
        description_header = soup.select_one("#product_description")
        if not description_header:
            return ""

        description = description_header.find_next_sibling("p")
        return description.get_text(strip=True) if description else ""

    def _parse_image_url(self, soup: BeautifulSoup, page_url: str) -> str:
        image = soup.select_one(".item.active img")
        return urljoin(
            page_url,
            self._attr_required(image, "src", "book image"),
        )

    def _parse_rating(self, rating: Tag | None) -> int:
        if not rating:
            raise ValueError("Missing book rating")

        for css_class in self._classes(rating):
            if css_class in RATING_MAP:
                return RATING_MAP[css_class]

        raise ValueError("Unknown book rating")

    def _parse_price(self, value: str) -> Decimal:
        cleaned = value.replace("£", "").strip()
        return Decimal(cleaned)

    def _parse_stock_count(self, value: str) -> int:
        match = search(r"\((\d+) available\)", value)
        return int(match.group(1)) if match else 0

    def _text_required(self, node: Tag | None, label: str) -> str:
        if not node:
            raise ValueError(f"Missing {label}")

        return node.get_text(strip=True)

    def _attr_required(
        self,
        node: PageElement | None,
        attr: str,
        label: str,
    ) -> str:
        if not isinstance(node, Tag):
            raise ValueError(f"Missing {label}")

        value = node.get(attr)
        if not isinstance(value, str) or not value:
            raise ValueError(f"Missing {label}")

        return value

    def _attr_optional(
        self,
        node: PageElement | None,
        attr: str,
    ) -> str | None:
        if not isinstance(node, Tag):
            return None

        value = node.get(attr)
        return value if isinstance(value, str) and value else None

    def _classes(self, node: Tag) -> list[str]:
        return cast(list[str], node.get_attribute_list("class"))

    def _required(self, value: object | None, label: str) -> str:
        if not isinstance(value, str) or not value:
            raise ValueError(f"Missing {label}")

        return value
