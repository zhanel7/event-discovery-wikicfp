"""User schemas."""

from uuid import UUID

from pydantic import BaseModel, EmailStr, Field


class UserBase(BaseModel):
    username: str = Field(..., min_length=3, max_length=150)
    email: EmailStr


class UserResponse(UserBase):
    id: UUID
    role: str
    is_active: bool

    model_config = {"from_attributes": True}


class UserUpdate(BaseModel):
    email: EmailStr | None = None
