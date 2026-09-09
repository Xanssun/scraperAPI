from taskiq_nats import PullBasedJetStreamBroker

from src.settings.core import Settings


def create_taskiq_broker(settings: Settings) -> PullBasedJetStreamBroker:
    return PullBasedJetStreamBroker(
        servers=settings.nats.servers,
        subject="scraper.tasks",
        queue="scraper-workers",
        user=settings.nats.user or None,
        password=settings.nats.password or None,
    )
