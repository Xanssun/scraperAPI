from taskiq import AsyncBroker

from src.tasks.scraper.task import setup_scraper_tasks


def setup_tasks(broker: AsyncBroker) -> None:
    setup_scraper_tasks(broker)
