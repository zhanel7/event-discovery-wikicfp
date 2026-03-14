"""Event service."""

import uuid
from datetime import date
from uuid import UUID

from app.core.exceptions import NotFoundError, ConflictError
from app.repositories.event import EventRepository
from app.repositories.category import CategoryRepository
from app.schemas.event import EventCreate, EventUpdate
from app.models.event import Event
from app.utils.slug import slugify


class EventService:
    def __init__(self, event_repo: EventRepository, category_repo: CategoryRepository):
        self.event_repo = event_repo
        self.category_repo = category_repo

    async def get_by_id_or_slug(self, id_or_slug: str | UUID) -> Event:
        event = await self.event_repo.get_by_id_or_slug(id_or_slug)
        if not event:
            raise NotFoundError("Event not found")
        return event

    async def list_events(
        self,
        *,
        search: str | None = None,
        category_id: UUID | None = None,
        country: str | None = None,
        city: str | None = None,
        mode: str | None = None,
        status: str | None = None,
        start_date_from: date | None = None,
        start_date_to: date | None = None,
        submission_deadline_from: date | None = None,
        submission_deadline_to: date | None = None,
        include_draft: bool = False,
        sort_by: str = "start_date",
        order: str = "asc",
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[list[Event], int]:
        skip = (page - 1) * page_size
        return await self.event_repo.list_events(
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
            include_draft=include_draft,
            sort_by=sort_by,
            order=order,
            skip=skip,
            limit=page_size,
        )

    async def create(self, data: EventCreate, created_by_id: UUID) -> Event:
        slug = slugify(data.title)
        if await self.event_repo.slug_exists(slug):
            slug = f"{slug}-{uuid.uuid4().hex[:8]}"
        event = Event(
            title=data.title,
            slug=slug,
            short_description=data.short_description,
            full_description=data.full_description,
            organizer=data.organizer,
            country=data.country,
            city=data.city,
            venue=data.venue,
            mode=data.mode,
            start_date=data.start_date,
            end_date=data.end_date,
            submission_deadline=data.submission_deadline,
            notification_deadline=data.notification_deadline,
            camera_ready_deadline=data.camera_ready_deadline,
            website_url=data.website_url,
            cfp_url=data.cfp_url,
            image_url=data.image_url,
            status=data.status,
            created_by_id=created_by_id,
        )
        await self.event_repo.create(event)
        if data.category_ids:
            await self.event_repo.set_categories(event.id, list(data.category_ids))
            await self.event_repo.session.refresh(event)
        return event

    async def update(self, id_or_slug: str | UUID, data: EventUpdate) -> Event:
        event = await self.get_by_id_or_slug(id_or_slug)
        kwargs = data.model_dump(exclude_unset=True)
        category_ids = kwargs.pop("category_ids", None)
        if "title" in kwargs and kwargs["title"]:
            new_slug = slugify(kwargs["title"])
            if await self.event_repo.slug_exists(new_slug, exclude_event_id=event.id):
                pass  # keep existing slug or append id
            else:
                kwargs["slug"] = new_slug
        await self.event_repo.update(event, **kwargs)
        if category_ids is not None:
            await self.event_repo.set_categories(event.id, category_ids)
        await self.event_repo.session.refresh(event)
        return event

    async def delete(self, id_or_slug: str | UUID) -> None:
        event = await self.get_by_id_or_slug(id_or_slug)
        await self.event_repo.delete(event)
