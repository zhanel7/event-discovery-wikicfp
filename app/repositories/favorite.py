"""Favorite repository."""

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.favorite import Favorite
from app.models.event import Event


class FavoriteRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_user_and_event(self, user_id: UUID, event_id: UUID) -> Favorite | None:
        result = await self.session.execute(
            select(Favorite).where(
                Favorite.user_id == user_id,
                Favorite.event_id == event_id,
            )
        )
        return result.scalar_one_or_none()

    async def list_by_user(self, user_id: UUID, skip: int = 0, limit: int = 100) -> list[Favorite]:
        result = await self.session.execute(
            select(Favorite)
            .options(
                selectinload(Favorite.event).selectinload(Event.category_links),
            )
            .where(Favorite.user_id == user_id)
            .order_by(Favorite.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        return list(result.unique().scalars().all())

    async def add(self, user_id: UUID, event_id: UUID) -> Favorite:
        fav = Favorite(user_id=user_id, event_id=event_id)
        self.session.add(fav)
        await self.session.flush()
        await self.session.refresh(fav)
        return fav

    async def remove(self, favorite: Favorite) -> None:
        await self.session.delete(favorite)
