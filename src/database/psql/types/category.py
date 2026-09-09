from typing import Literal, TypedDict

CategoryLoads = Literal["books"]


class CreateCategoryType(TypedDict):
    name: str


class UpdateCategoryType(TypedDict, total=False):
    name: str | None
