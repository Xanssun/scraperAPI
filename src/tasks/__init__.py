from taskiq import AsyncBroker

from src.tasks.books import setup_books_tasks


def setup_tasks(broker: AsyncBroker) -> None:
    setup_books_tasks(broker)
