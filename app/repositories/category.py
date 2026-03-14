"""Category repository."""

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.category import Category


class CategoryRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, category_id: UUID) -> Category | None:
        result = await self.session.execute(select(Category).where(Category.id == category_id))
        return result.scalar_one_or_none()

    async def get_by_slug(self, slug: str) -> Category | None:
        result = await self.session.execute(select(Category).where(Category.slug == slug))
        return result.scalar_one_or_none()

    async def get_by_id_or_slug(self, id_or_slug: str | UUID) -> Category | None:
        if isinstance(id_or_slug, UUID):
            return await self.get_by_id(id_or_slug)
        return await self.get_by_slug(id_or_slug)

    async def list_all(self) -> list[Category]:
        result = await self.session.execute(select(Category).order_by(Category.name))
        return list(result.scalars().all())

    async def create(self, name: str, slug: str, description: str | None = None) -> Category:
        cat = Category(name=name, slug=slug, description=description)
        self.session.add(cat)
        await self.session.flush()
        await self.session.refresh(cat)
        return cat

    async def update(self, category: Category, **kwargs: object) -> Category:
        for k, v in kwargs.items():
            if hasattr(category, k):
                setattr(category, k, v)
        await self.session.flush()
        await self.session.refresh(category)
        return category

    async def delete(self, category: Category) -> None:
        await self.session.delete(category)
