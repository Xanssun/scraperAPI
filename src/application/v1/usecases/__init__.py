from src.application.common.bus import RequestBusImpl

from . import book, category, scrape


def setup_use_cases(request_bus: RequestBusImpl) -> None:
    request_bus.register(category.SelectManyCategoriesRequest, category.SelectManyCategoriesUseCase)

    request_bus.register(book.SelectBookRequest, book.SelectBookUseCase)
    request_bus.register(book.SelectManyBooksRequest, book.SelectManyBooksUseCase)

    request_bus.register(scrape.SelectScrapeRunRequest, scrape.SelectScrapeRunUseCase)
    request_bus.register(
        scrape.SelectManyScrapeRunsRequest,
        scrape.SelectManyScrapeRunsUseCase,
    )
    request_bus.register(scrape.StartBooksScrapeRequest, scrape.StartBooksScrapeUseCase)
