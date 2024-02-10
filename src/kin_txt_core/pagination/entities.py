from typing import Generic, TypeVar

from pydantic import ConfigDict, BaseModel, Field

T = TypeVar("T", bound=BaseModel)


class PaginatedDataEntity(BaseModel, Generic[T]):
    data: list[T]
    total_pages: int = Field(..., alias="totalPages")
    page: int

    model_config = ConfigDict(populate_by_name=True)
