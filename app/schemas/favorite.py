"""Favorite schemas."""

from uuid import UUID

from pydantic import BaseModel, Field


class FavoriteCreate(BaseModel):
    event_id: UUID


class FavoriteResponse(BaseModel):
    id: UUID
    user_id: UUID
    event_id: UUID

    model_config = {"from_attributes": True}
