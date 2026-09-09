import structlog
from dishka.integrations.taskiq import TaskiqProvider, setup_dishka
from taskiq import AsyncBroker, TaskiqEvents, TaskiqState

from src.entrypoints.container import build_container
from src.settings.core import Settings, load_settings
from src.tasks import setup_tasks
from src.tasks.broker import create_taskiq_broker

log = structlog.get_logger(__name__)


def create_tasks(settings: Settings) -> AsyncBroker:
    log.info("Initialize tasks (Taskiq) application")

    broker = create_taskiq_broker(settings)

    container = build_container(settings, TaskiqProvider())
    setup_dishka(container, broker)

    async def on_startup(state: TaskiqState) -> None:
        log.info("Taskiq application started")

    async def on_shutdown(state: TaskiqState) -> None:
        log.info("Taskiq application shutting down")
        await container.close()

    broker.add_event_handler(TaskiqEvents.WORKER_STARTUP, on_startup)
    broker.add_event_handler(TaskiqEvents.CLIENT_STARTUP, on_startup)
    broker.add_event_handler(TaskiqEvents.WORKER_SHUTDOWN, on_shutdown)
    broker.add_event_handler(TaskiqEvents.CLIENT_SHUTDOWN, on_shutdown)

    setup_tasks(broker)

    return broker


settings = load_settings()
broker = create_tasks(settings)
