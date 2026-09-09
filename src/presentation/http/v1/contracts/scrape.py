from datetime import datetime
from typing import Annotated

import uuid_utils.compat as uuid
from pydantic import Field, model_validator

from src.database.psql.models.types import ScrapeRunStatus
from src.presentation.http.common.contract import Contract


class StartBooksScrape(Contract):
    start_page: Annotated[int, Field(ge=1)] = 1
    end_page: Annotated[int, Field(ge=1)] = 50
    concurrency: Annotated[int, Field(ge=1, le=10)] = 10

    @model_validator(mode="after")
    def validate_pages_range(self) -> "StartBooksScrape":
        if self.end_page < self.start_page:
            raise ValueError("end_page must be greater than or equal to start_page")

        return self


class ScrapeRun(Contract):
    uuid: uuid.UUID
    started_at: datetime
    finished_at: datetime | None = None
    state: ScrapeRunStatus
    processed_count: int
    created_count: int
    updated_count: int
    error_count: int


class SelectScrapeRuns(Contract):
    state: ScrapeRunStatus | None = None
    started_from: datetime | None = None
    started_to: datetime | None = None

    @model_validator(mode="after")
    def validate_started_range(self) -> "SelectScrapeRuns":
        if (
            self.started_from is not None
            and self.started_to is not None
            and self.started_to < self.started_from
        ):
            raise ValueError("started_to must be greater than or equal to started_from")

        return self
