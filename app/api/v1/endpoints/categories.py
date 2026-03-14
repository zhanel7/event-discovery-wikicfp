"""Category endpoints: list, get, create, update, delete."""

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends

from app.api.deps import get_current_admin
from app.db.session import get_db
from app.models.user import User
from app.repositories.category import CategoryRepository
from app.schemas.category import CategoryCreate, CategoryUpdate, CategoryResponse
from app.services.category import CategoryService

router = APIRouter(prefix="/categories", tags=["categories"])


def get_category_service(session=Depends(get_db)) -> CategoryService:
    return CategoryService(CategoryRepository(session))


@router.get("", response_model=list[CategoryResponse])
async def list_categories(
    service: CategoryService = Depends(get_category_service),
):
    """List all categories. Public."""
    categories = await service.list_all()
    return [CategoryResponse.model_validate(c) for c in categories]


@router.get("/{id_or_slug}", response_model=CategoryResponse)
async def get_category(
    id_or_slug: str | UUID,
    service: CategoryService = Depends(get_category_service),
):
    """Get category by ID or slug. Public."""
    cat = await service.get_by_id_or_slug(id_or_slug)
    return CategoryResponse.model_validate(cat)


@router.post("", response_model=CategoryResponse, status_code=201)
async def create_category(
    data: CategoryCreate,
    current_user: Annotated[User, Depends(get_current_admin)],
    service: CategoryService = Depends(get_category_service),
):
    """Create category. Admin only."""
    cat = await service.create(data)
    return CategoryResponse.model_validate(cat)


@router.patch("/{id_or_slug}", response_model=CategoryResponse)
async def update_category(
    id_or_slug: str | UUID,
    data: CategoryUpdate,
    current_user: Annotated[User, Depends(get_current_admin)],
    service: CategoryService = Depends(get_category_service),
):
    """Update category. Admin only."""
    cat = await service.update(id_or_slug, data)
    return CategoryResponse.model_validate(cat)


@router.delete("/{id_or_slug}", status_code=204)
async def delete_category(
    id_or_slug: str | UUID,
    current_user: Annotated[User, Depends(get_current_admin)],
    service: CategoryService = Depends(get_category_service),
):
    """Delete category. Admin only."""
    await service.delete(id_or_slug)
