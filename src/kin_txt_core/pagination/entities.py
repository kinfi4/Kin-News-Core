from typing import Generic, TypeVar

from pydantic import BaseModel, Field

T = TypeVar("T", bound=BaseModel)


class PaginatedDataEntity(BaseModel, Generic[T]):
    data: list[T]
    total_pages: int = Field(..., alias="totalPages")
    page: int

    class Config:
        allow_population_by_field_name = True
