"""Event and EventCategory models."""

import uuid
from datetime import date, datetime
from typing import TYPE_CHECKING

from sqlalchemy import Date, DateTime, ForeignKey, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, relationship, mapped_column

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.category import Category
    from app.models.favorite import Favorite


class EventMode(str, __import__("enum").Enum):
    online = "online"
    offline = "offline"
    hybrid = "hybrid"


class EventStatus(str, __import__("enum").Enum):
    draft = "draft"
    published = "published"
    archived = "archived"


class Event(Base):
    __tablename__ = "events"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    title: Mapped[str] = mapped_column(String(500), nullable=False, index=True)
    slug: Mapped[str] = mapped_column(String(500), unique=True, nullable=False, index=True)
    short_description: Mapped[str | None] = mapped_column(Text, nullable=True)
    full_description: Mapped[str | None] = mapped_column(Text, nullable=True)
    organizer: Mapped[str | None] = mapped_column(String(500), nullable=True)
    country: Mapped[str | None] = mapped_column(String(255), nullable=True, index=True)
    city: Mapped[str | None] = mapped_column(String(255), nullable=True, index=True)
    venue: Mapped[str | None] = mapped_column(String(500), nullable=True)
    mode: Mapped[str] = mapped_column(String(20), nullable=False, default=EventMode.offline.value, index=True)
    start_date: Mapped[date | None] = mapped_column(Date, nullable=True, index=True)
    end_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    submission_deadline: Mapped[date | None] = mapped_column(Date, nullable=True, index=True)
    notification_deadline: Mapped[date | None] = mapped_column(Date, nullable=True)
    camera_ready_deadline: Mapped[date | None] = mapped_column(Date, nullable=True)
    website_url: Mapped[str | None] = mapped_column(String(2000), nullable=True)
    cfp_url: Mapped[str | None] = mapped_column(String(2000), nullable=True)
    image_url: Mapped[str | None] = mapped_column(String(2000), nullable=True)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default=EventStatus.published.value, index=True)
    created_by_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    created_by_user: Mapped["User | None"] = relationship("User", back_populates="events")
    category_links: Mapped[list["EventCategory"]] = relationship(
        "EventCategory", back_populates="event", cascade="all, delete-orphan"
    )
    favorites: Mapped[list["Favorite"]] = relationship("Favorite", back_populates="event")

    def __repr__(self) -> str:
        return f"<Event {self.slug}>"


class EventCategory(Base):
    __tablename__ = "event_categories"

    event_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("events.id", ondelete="CASCADE"), primary_key=True
    )
    category_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("categories.id", ondelete="CASCADE"), primary_key=True
    )

    event: Mapped["Event"] = relationship("Event", back_populates="category_links")
    category: Mapped["Category"] = relationship("Category", back_populates="event_associations")
