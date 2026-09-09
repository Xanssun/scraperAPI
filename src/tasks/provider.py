from collections.abc import AsyncIterator

from dishka import Provider, Scope, provide
from taskiq import AsyncBroker

from src.application.common.interfaces.scrape_tasks import ScrapeTaskProducer
from src.settings.core import Settings
from src.tasks import setup_tasks
from src.tasks.broker import create_taskiq_broker
from src.tasks.producer import TaskiqScrapeTaskProducer


class TasksProvider(Provider):
    scope = Scope.APP

    @provide
    async def taskiq_broker(self, settings: Settings) -> AsyncIterator[AsyncBroker]:
        broker = create_taskiq_broker(settings)
        setup_tasks(broker)
        await broker.startup()
        try:
            yield broker
        finally:
            await broker.shutdown()

    @provide
    def scrape_task_producer(self, broker: AsyncBroker) -> ScrapeTaskProducer:
        return TaskiqScrapeTaskProducer(broker)
