from fastapi import APIRouter, FastAPI

from .book import book_router
from .category import category_router
from .scrape import scrape_router


def setup_v1_routers(app: FastAPI) -> None:
    router = APIRouter(prefix="/v1")

    router.include_router(book_router)
    router.include_router(category_router)
    router.include_router(scrape_router)

    app.include_router(router)
