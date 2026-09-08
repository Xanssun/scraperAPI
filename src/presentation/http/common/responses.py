from typing import Any

from starlette.responses import JSONResponse

from src.presentation.http.common.serializers.orjson import orjson_dumps


class ORJSONResponse(JSONResponse):
    media_type = "application/json"

    def render(self, content: Any) -> bytes:
        return orjson_dumps(content)
