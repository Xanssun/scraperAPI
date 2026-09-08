from typing import Any, Dict, Union
from uuid import UUID

from pydantic import BaseModel


def _predict_bytes(value: Any) -> bytes | None:
    match value:
        case str():
            return value.encode()
        case bytes():
            return value
        case _:
            return None


def _default(value: Any) -> Union[str, Dict[str, Any]] | None:
    match value:
        case BaseModel():
            return value.model_dump(mode="json", exclude_none=True, by_alias=True)
        case UUID():
            return str(value)
        case Exception():
            return value.args[0] if len(value.args) > 0 else "Unknown error"
        case _:
            return None
