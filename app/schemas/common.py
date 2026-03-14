"""Common response schemas: pagination, error."""

from typing import Generic, TypeVar

from pydantic import BaseModel, Field

T = TypeVar("T")


class PaginationMeta(BaseModel):
    total: int = Field(..., description="Total number of items")
    page: int = Field(..., ge=1, description="Current page")
    page_size: int = Field(..., ge=1, le=100, description="Page size")
    total_pages: int = Field(..., ge=0, description="Total pages")


class PaginatedResponse(BaseModel, Generic[T]):
    items: list[T] = Field(default_factory=list)
    meta: PaginationMeta


def pagination_meta(total: int, page: int, page_size: int) -> PaginationMeta:
    total_pages = (total + page_size - 1) // page_size if page_size else 0
    return PaginationMeta(total=total, page=page, page_size=page_size, total_pages=total_pages)
