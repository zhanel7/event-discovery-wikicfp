"""Favorites (bookmarks) endpoints."""

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.repositories.favorite import FavoriteRepository
from app.repositories.event import EventRepository
from app.schemas.favorite import FavoriteCreate, FavoriteResponse
from app.schemas.event import EventListResponse
from app.services.favorite import FavoriteService

router = APIRouter(prefix="/favorites", tags=["favorites"])


def get_favorite_service(session=Depends(get_db)) -> FavoriteService:
    return FavoriteService(FavoriteRepository(session), EventRepository(session))


@router.get("", response_model=list[EventListResponse])
async def list_favorites(
    current_user: Annotated[User, Depends(get_current_user)],
    service: FavoriteService = Depends(get_favorite_service),
):
    """List current user's favorite events."""
    favorites = await service.list_for_user(current_user.id)
    return [
        EventListResponse(
            id=f.event.id,
            title=f.event.title,
            slug=f.event.slug,
            short_description=f.event.short_description,
            organizer=f.event.organizer,
            country=f.event.country,
            city=f.event.city,
            mode=f.event.mode,
            start_date=f.event.start_date,
            end_date=f.event.end_date,
            submission_deadline=f.event.submission_deadline,
            status=f.event.status,
            category_ids=[link.category_id for link in f.event.category_links],
        )
        for f in favorites
    ]


@router.post("", status_code=201)
async def add_favorite(
    data: FavoriteCreate,
    current_user: Annotated[User, Depends(get_current_user)],
    service: FavoriteService = Depends(get_favorite_service),
):
    """Add event to favorites."""
    await service.add(current_user.id, data.event_id)
    return {"message": "Added to favorites"}


@router.delete("/{event_id}", status_code=204)
async def remove_favorite(
    event_id: UUID,
    current_user: Annotated[User, Depends(get_current_user)],
    service: FavoriteService = Depends(get_favorite_service),
):
    """Remove event from favorites."""
    await service.remove(current_user.id, event_id)
