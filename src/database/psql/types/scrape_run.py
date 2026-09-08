from datetime import datetime
from typing import TypedDict

from src.database.psql.models.types import ScrapeRunStatus


class CreateScrapeRunType(TypedDict, total=False):
    started_at: datetime
    state: ScrapeRunStatus
    processed_count: int
    created_count: int
    updated_count: int
    error_count: int


class UpdateScrapeRunType(TypedDict, total=False):
    finished_at: datetime | None
    state: ScrapeRunStatus
    processed_count: int
    created_count: int
    updated_count: int
    error_count: int
