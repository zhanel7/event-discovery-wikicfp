"""Initial schema: users, events, categories, event_categories, favorites.

Revision ID: 001
Revises:
Create Date: 2025-01-01 00:00:00

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("username", sa.String(150), nullable=False),
        sa.Column("email", sa.String(255), nullable=False),
        sa.Column("hashed_password", sa.String(255), nullable=False),
        sa.Column("role", sa.String(20), nullable=False, server_default="user"),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_users_username", "users", ["username"], unique=True)
    op.create_index("ix_users_email", "users", ["email"], unique=True)

    op.create_table(
        "categories",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("slug", sa.String(255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_categories_slug", "categories", ["slug"], unique=True)

    op.create_table(
        "events",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("title", sa.String(500), nullable=False),
        sa.Column("slug", sa.String(500), nullable=False),
        sa.Column("short_description", sa.Text(), nullable=True),
        sa.Column("full_description", sa.Text(), nullable=True),
        sa.Column("organizer", sa.String(500), nullable=True),
        sa.Column("country", sa.String(255), nullable=True),
        sa.Column("city", sa.String(255), nullable=True),
        sa.Column("venue", sa.String(500), nullable=True),
        sa.Column("mode", sa.String(20), nullable=False, server_default="offline"),
        sa.Column("start_date", sa.Date(), nullable=True),
        sa.Column("end_date", sa.Date(), nullable=True),
        sa.Column("submission_deadline", sa.Date(), nullable=True),
        sa.Column("notification_deadline", sa.Date(), nullable=True),
        sa.Column("camera_ready_deadline", sa.Date(), nullable=True),
        sa.Column("website_url", sa.String(2000), nullable=True),
        sa.Column("cfp_url", sa.String(2000), nullable=True),
        sa.Column("image_url", sa.String(2000), nullable=True),
        sa.Column("status", sa.String(20), nullable=False, server_default="published"),
        sa.Column("created_by_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["created_by_id"], ["users.id"], ondelete="SET NULL"),
    )
    op.create_index("ix_events_slug", "events", ["slug"], unique=True)
    op.create_index("ix_events_start_date", "events", ["start_date"], unique=False)
    op.create_index("ix_events_submission_deadline", "events", ["submission_deadline"], unique=False)
    op.create_index("ix_events_status", "events", ["status"], unique=False)
    op.create_index("ix_events_country", "events", ["country"], unique=False)
    op.create_index("ix_events_mode", "events", ["mode"], unique=False)
    op.create_index("ix_events_created_by_id", "events", ["created_by_id"], unique=False)

    op.create_table(
        "event_categories",
        sa.Column("event_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("category_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.PrimaryKeyConstraint("event_id", "category_id"),
        sa.ForeignKeyConstraint(["event_id"], ["events.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["category_id"], ["categories.id"], ondelete="CASCADE"),
    )

    op.create_table(
        "favorites",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("event_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id", "event_id", name="uq_favorites_user_event"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["event_id"], ["events.id"], ondelete="CASCADE"),
    )
    op.create_index("ix_favorites_user_id", "favorites", ["user_id"], unique=False)
    op.create_index("ix_favorites_event_id", "favorites", ["event_id"], unique=False)


def downgrade() -> None:
    op.drop_table("favorites")
    op.drop_table("event_categories")
    op.drop_table("events")
    op.drop_table("categories")
    op.drop_table("users")
