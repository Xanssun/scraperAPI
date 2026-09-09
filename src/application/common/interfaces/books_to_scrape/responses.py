from pydantic import BaseModel, ConfigDict


class HtmlPageResponse(BaseModel):
    model_config = ConfigDict(frozen=True)

    url: str
    html: str


class CatalogPageResponse(HtmlPageResponse):
    page: int


class BookPageResponse(HtmlPageResponse):
    pass
