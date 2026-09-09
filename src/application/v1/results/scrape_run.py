from datetime import datetime

import uuid_utils.compat as uuid

from src.application.v1.results.base import Result
from src.database.psql.models.types import ScrapeRunStatus


class ScrapeRunResult(Result):
    uuid: uuid.UUID
    started_at: datetime
    finished_at: datetime | None = None
    state: ScrapeRunStatus
    processed_count: int
    created_count: int
    updated_count: int
    error_count: int
