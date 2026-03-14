"""Favorites service."""

from uuid import UUID

from app.core.exceptions import NotFoundError, ConflictError
from app.repositories.favorite import FavoriteRepository
from app.repositories.event import EventRepository


class FavoriteService:
    def __init__(self, favorite_repo: FavoriteRepository, event_repo: EventRepository):
        self.favorite_repo = favorite_repo
        self.event_repo = event_repo

    async def add(self, user_id: UUID, event_id: UUID) -> None:
        event = await self.event_repo.get_by_id(event_id)
        if not event:
            raise NotFoundError("Event not found")
        existing = await self.favorite_repo.get_by_user_and_event(user_id, event_id)
        if existing:
            raise ConflictError("Event already in favorites")
        await self.favorite_repo.add(user_id, event_id)

    async def remove(self, user_id: UUID, event_id: UUID) -> None:
        fav = await self.favorite_repo.get_by_user_and_event(user_id, event_id)
        if not fav:
            raise NotFoundError("Favorite not found")
        await self.favorite_repo.remove(fav)

    async def list_for_user(self, user_id: UUID, skip: int = 0, limit: int = 100) -> list:
        return await self.favorite_repo.list_by_user(user_id, skip=skip, limit=limit)
