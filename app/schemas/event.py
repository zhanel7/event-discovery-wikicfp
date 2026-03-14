"""Event schemas."""

from datetime import date, datetime
from uuid import UUID

from pydantic import BaseModel, Field


class EventBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=500)
    short_description: str | None = None
    full_description: str | None = None
    organizer: str | None = None
    country: str | None = None
    city: str | None = None
    venue: str | None = None
    mode: str = Field(default="offline", pattern="^(online|offline|hybrid)$")
    start_date: date | None = None
    end_date: date | None = None
    submission_deadline: date | None = None
    notification_deadline: date | None = None
    camera_ready_deadline: date | None = None
    website_url: str | None = None
    cfp_url: str | None = None
    image_url: str | None = None
    status: str = Field(default="published", pattern="^(draft|published|archived)$")


class EventCreate(EventBase):
    category_ids: list[UUID] = Field(default_factory=list)


class EventUpdate(BaseModel):
    title: str | None = Field(None, min_length=1, max_length=500)
    short_description: str | None = None
    full_description: str | None = None
    organizer: str | None = None
    country: str | None = None
    city: str | None = None
    venue: str | None = None
    mode: str | None = Field(None, pattern="^(online|offline|hybrid)$")
    start_date: date | None = None
    end_date: date | None = None
    submission_deadline: date | None = None
    notification_deadline: date | None = None
    camera_ready_deadline: date | None = None
    website_url: str | None = None
    cfp_url: str | None = None
    image_url: str | None = None
    status: str | None = Field(None, pattern="^(draft|published|archived)$")
    category_ids: list[UUID] | None = None


class EventListResponse(BaseModel):
    id: UUID
    title: str
    slug: str
    short_description: str | None
    organizer: str | None
    country: str | None
    city: str | None
    mode: str
    start_date: date | None
    end_date: date | None
    submission_deadline: date | None
    status: str
    category_ids: list[UUID] = Field(default_factory=list)

    model_config = {"from_attributes": True}


class EventDetailResponse(EventBase):
    id: UUID
    slug: str
    created_by_id: UUID | None
    created_at: datetime
    updated_at: datetime
    category_ids: list[UUID] = Field(default_factory=list)

    model_config = {"from_attributes": True}
