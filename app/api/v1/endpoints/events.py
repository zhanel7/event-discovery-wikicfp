"""Event endpoints: list, get, create, update, delete."""

from datetime import date
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Query

from app.api.deps import get_current_user, get_current_admin
from app.db.session import get_db
from app.models.user import User
from app.repositories.event import EventRepository
from app.repositories.category import CategoryRepository
from app.schemas.common import PaginatedResponse, PaginationMeta, pagination_meta
from app.schemas.event import (
    EventCreate,
    EventUpdate,
    EventListResponse,
    EventDetailResponse,
)
from app.services.event import EventService

router = APIRouter(prefix="/events", tags=["events"])


def get_event_service(session=Depends(get_db)) -> EventService:
    return EventService(EventRepository(session), CategoryRepository(session))


def _event_to_list_response(event) -> EventListResponse:
    return EventListResponse(
        id=event.id,
        title=event.title,
        slug=event.slug,
        short_description=event.short_description,
        organizer=event.organizer,
        country=event.country,
        city=event.city,
        mode=event.mode,
        start_date=event.start_date,
        end_date=event.end_date,
        submission_deadline=event.submission_deadline,
        status=event.status,
        category_ids=[link.category_id for link in event.category_links],
    )


def _event_to_detail_response(event) -> EventDetailResponse:
    return EventDetailResponse(
        id=event.id,
        slug=event.slug,
        title=event.title,
        short_description=event.short_description,
        full_description=event.full_description,
        organizer=event.organizer,
        country=event.country,
        city=event.city,
        venue=event.venue,
        mode=event.mode,
        start_date=event.start_date,
        end_date=event.end_date,
        submission_deadline=event.submission_deadline,
        notification_deadline=event.notification_deadline,
        camera_ready_deadline=event.camera_ready_deadline,
        website_url=event.website_url,
        cfp_url=event.cfp_url,
        image_url=event.image_url,
        status=event.status,
        created_by_id=event.created_by_id,
        created_at=event.created_at,
        updated_at=event.updated_at,
        category_ids=[link.category_id for link in event.category_links],
    )


@router.get("", response_model=PaginatedResponse[EventListResponse])
async def list_events(
    service: EventService = Depends(get_event_service),
    search: str | None = Query(None, alias="q", description="Search in title, description, organizer"),
    category_id: UUID | None = Query(None, description="Filter by category"),
    country: str | None = None,
    city: str | None = None,
    mode: str | None = Query(None, pattern="^(online|offline|hybrid)$"),
    status: str | None = Query(None, description="Filter by status (admin may use)"),
    start_date_from: date | None = None,
    start_date_to: date | None = None,
    submission_deadline_from: date | None = None,
    submission_deadline_to: date | None = None,
    sort: str = Query("start_date", pattern="^(start_date|submission_deadline|created_at|title)$"),
    order: str = Query("asc", pattern="^(asc|desc)$"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
):
    """List events with search, filters, sort, and pagination. Public."""
    events, total = await service.list_events(
        search=search,
        category_id=category_id,
        country=country,
        city=city,
        mode=mode,
        status=status,
        start_date_from=start_date_from,
        start_date_to=start_date_to,
        submission_deadline_from=submission_deadline_from,
        submission_deadline_to=submission_deadline_to,
        include_draft=False,
        sort_by=sort,
        order=order,
        page=page,
        page_size=page_size,
    )
    meta = pagination_meta(total, page, page_size)
    return PaginatedResponse(
        items=[_event_to_list_response(e) for e in events],
        meta=meta,
    )


@router.get("/{id_or_slug}", response_model=EventDetailResponse)
async def get_event(
    id_or_slug: str | UUID,
    service: EventService = Depends(get_event_service),
):
    """Get event by ID or slug. Public."""
    event = await service.get_by_id_or_slug(id_or_slug)
    return _event_to_detail_response(event)


@router.post("", response_model=EventDetailResponse, status_code=201)
async def create_event(
    data: EventCreate,
    current_user: Annotated[User, Depends(get_current_admin)],
    service: EventService = Depends(get_event_service),
):
    """Create event. Admin only."""
    event = await service.create(data, current_user.id)
    return _event_to_detail_response(event)


@router.patch("/{id_or_slug}", response_model=EventDetailResponse)
async def update_event(
    id_or_slug: str | UUID,
    data: EventUpdate,
    current_user: Annotated[User, Depends(get_current_admin)],
    service: EventService = Depends(get_event_service),
):
    """Update event. Admin only."""
    event = await service.update(id_or_slug, data)
    return _event_to_detail_response(event)


@router.delete("/{id_or_slug}", status_code=204)
async def delete_event(
    id_or_slug: str | UUID,
    current_user: Annotated[User, Depends(get_current_admin)],
    service: EventService = Depends(get_event_service),
):
    """Delete event. Admin only."""
    await service.delete(id_or_slug)
