"""Category service."""

from uuid import UUID

from app.core.exceptions import NotFoundError, ConflictError
from app.repositories.category import CategoryRepository
from app.schemas.category import CategoryCreate, CategoryUpdate
from app.models.category import Category


class CategoryService:
    def __init__(self, category_repo: CategoryRepository):
        self.category_repo = category_repo

    async def get_by_id_or_slug(self, id_or_slug: str | UUID) -> Category:
        cat = await self.category_repo.get_by_id_or_slug(id_or_slug)
        if not cat:
            raise NotFoundError("Category not found")
        return cat

    async def list_all(self) -> list[Category]:
        return await self.category_repo.list_all()

    async def create(self, data: CategoryCreate) -> Category:
        existing = await self.category_repo.get_by_slug(data.slug)
        if existing:
            raise ConflictError("Category slug already exists")
        return await self.category_repo.create(
            name=data.name,
            slug=data.slug,
            description=data.description,
        )

    async def update(self, id_or_slug: str | UUID, data: CategoryUpdate) -> Category:
        cat = await self.get_by_id_or_slug(id_or_slug)
        if data.slug is not None:
            existing = await self.category_repo.get_by_slug(data.slug)
            if existing and existing.id != cat.id:
                raise ConflictError("Category slug already exists")
        kwargs = data.model_dump(exclude_unset=True)
        return await self.category_repo.update(cat, **kwargs)

    async def delete(self, id_or_slug: str | UUID) -> None:
        cat = await self.get_by_id_or_slug(id_or_slug)
        await self.category_repo.delete(cat)
