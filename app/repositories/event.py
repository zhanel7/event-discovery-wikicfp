"""Event repository: list, filter, search, sort, paginate."""

from datetime import date
from uuid import UUID

from sqlalchemy import select, func, or_, and_, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.event import Event, EventCategory
from app.models.category import Category


class EventRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, event_id: UUID) -> Event | None:
        result = await self.session.execute(
            select(Event).where(Event.id == event_id).options(selectinload(Event.category_links))
        )
        return result.scalar_one_or_none()

    async def get_by_slug(self, slug: str) -> Event | None:
        result = await self.session.execute(
            select(Event).where(Event.slug == slug).options(selectinload(Event.category_links))
        )
        return result.scalar_one_or_none()

    async def get_by_id_or_slug(self, id_or_slug: str | UUID) -> Event | None:
        if isinstance(id_or_slug, UUID):
            return await self.get_by_id(id_or_slug)
        return await self.get_by_slug(id_or_slug)

    async def slug_exists(self, slug: str, exclude_event_id: UUID | None = None) -> bool:
        q = select(Event.id).where(Event.slug == slug)
        if exclude_event_id:
            q = q.where(Event.id != exclude_event_id)
        result = await self.session.execute(q)
        return result.scalar_one_or_none() is not None

    def _build_filters(
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
    ):
        """Return base select and filter list for reuse in list and count."""
        base = select(Event)
        if not include_draft:
            base = base.where(Event.status == "published")
        elif status:
            base = base.where(Event.status == status)
        if search:
            term = f"%{search}%"
            base = base.where(
                or_(
                    Event.title.ilike(term),
                    Event.short_description.ilike(term),
                    Event.full_description.ilike(term),
                    Event.organizer.ilike(term),
                )
            )
        if category_id:
            base = base.join(EventCategory).where(EventCategory.category_id == category_id)
        if country:
            base = base.where(Event.country == country)
        if city:
            base = base.where(Event.city == city)
        if mode:
            base = base.where(Event.mode == mode)
        if start_date_from:
            base = base.where(Event.start_date >= start_date_from)
        if start_date_to:
            base = base.where(Event.start_date <= start_date_to)
        if submission_deadline_from:
            base = base.where(Event.submission_deadline >= submission_deadline_from)
        if submission_deadline_to:
            base = base.where(Event.submission_deadline <= submission_deadline_to)
        return base

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
        skip: int = 0,
        limit: int = 20,
    ) -> tuple[list[Event], int]:
        base = self._build_filters(
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
        )
        # Count distinct event ids (needed when category join produces duplicate rows)
        id_subq = base.with_only_columns(Event.id).distinct().subquery()
        count_q = select(func.count()).select_from(id_subq)
        total_result = await self.session.execute(count_q)
        total = total_result.scalar() or 0
        # List with options and sort
        q = base.options(selectinload(Event.category_links))
        sort_column = {
            "start_date": Event.start_date,
            "submission_deadline": Event.submission_deadline,
            "created_at": Event.created_at,
            "title": Event.title,
        }.get(sort_by, Event.start_date)
        if order == "desc":
            q = q.order_by(sort_column.desc().nullslast())
        else:
            q = q.order_by(sort_column.asc().nullsfirst())
        q = q.offset(skip).limit(limit)
        result = await self.session.execute(q)
        return list(result.unique().scalars().all()), total

    async def create(self, event: Event) -> Event:
        self.session.add(event)
        await self.session.flush()
        await self.session.refresh(event)
        return event

    async def set_categories(self, event_id: UUID, category_ids: list[UUID]) -> None:
        await self.session.execute(delete(EventCategory).where(EventCategory.event_id == event_id))
        for cid in category_ids:
            self.session.add(EventCategory(event_id=event_id, category_id=cid))
        await self.session.flush()

    async def update(self, event: Event, **kwargs: object) -> Event:
        for k, v in kwargs.items():
            if hasattr(event, k):
                setattr(event, k, v)
        await self.session.flush()
        await self.session.refresh(event)
        return event

    async def delete(self, event: Event) -> None:
        await self.session.delete(event)
