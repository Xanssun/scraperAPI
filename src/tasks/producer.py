import uuid_utils.compat as uuid
from taskiq import AsyncBroker

from src.application.common.interfaces.scrape_tasks import ScrapeTaskProducer
from src.tasks.books import BOOKS_SCRAPE_TASK_NAME


class TaskiqScrapeTaskProducer(ScrapeTaskProducer):
    __slots__ = ("_broker",)

    def __init__(self, broker: AsyncBroker) -> None:
        self._broker = broker

    async def enqueue_books_scrape(
        self,
        run_uuid: uuid.UUID,
        *,
        start_page: int,
        end_page: int,
        concurrency: int,
    ) -> None:
        task = self._broker.find_task(BOOKS_SCRAPE_TASK_NAME)
        if task is None:
            raise RuntimeError(f"Task `{BOOKS_SCRAPE_TASK_NAME}` is not registered")

        await task.kiq(
            str(run_uuid),
            start_page=start_page,
            end_page=end_page,
            concurrency=concurrency,
        )
