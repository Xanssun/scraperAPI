import asyncio
from collections.abc import Collection
from http import HTTPStatus
from typing import Any

from src.infrastructure.http.provider import errors as err
from src.infrastructure.http.provider.middleware.base import (
    BaseRequestMiddleware,
    CallNextMiddlewareType,
)
from src.infrastructure.http.provider.response import Response
from src.infrastructure.http.provider.types import RequestMethodType


class RetryMiddleware(BaseRequestMiddleware):
    __slots__ = ("_attempts", "_base_delay", "_retry_methods")

    def __init__(
        self,
        attempts: int = 3,
        base_delay: float = 0.3,
        retry_methods: Collection[RequestMethodType] = ("GET", "HEAD", "OPTIONS"),
    ) -> None:
        self._attempts = attempts
        self._base_delay = base_delay
        self._retry_methods = frozenset(retry_methods)

    async def __call__(
        self,
        call_next: CallNextMiddlewareType,
        method: RequestMethodType,
        url_or_endpoint: str,
        **kw: Any,
    ) -> Response:
        if method not in self._retry_methods:
            return await call_next(
                method=method,
                url_or_endpoint=url_or_endpoint,
                **kw,
            )

        for attempt in range(1, self._attempts + 1):
            try:
                return await call_next(
                    method=method,
                    url_or_endpoint=url_or_endpoint,
                    **kw,
                )
            except Exception as exc:
                if attempt >= self._attempts or not self._can_retry(exc):
                    raise

                await asyncio.sleep(self._base_delay * 2 ** (attempt - 1))

        raise RuntimeError("unreachable retry state")

    def _can_retry(self, exc: Exception) -> bool:
        if isinstance(exc, err.NetworkError):
            return True
        if isinstance(exc, err.APIError):
            return HTTPStatus.INTERNAL_SERVER_ERROR <= exc.status_code

        return False
