"""User profile endpoints: me."""

from typing import Annotated

from fastapi import APIRouter, Depends

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.repositories.user import UserRepository
from app.schemas.user import UserResponse, UserUpdate
from app.services.user import UserService

router = APIRouter(prefix="/users", tags=["users"])


def get_user_service(session=Depends(get_db)) -> UserService:
    return UserService(UserRepository(session))


@router.get("/me", response_model=UserResponse)
async def get_me(
    current_user: Annotated[User, Depends(get_current_user)],
):
    """Get current user profile."""
    return UserResponse.model_validate(current_user)


@router.patch("/me", response_model=UserResponse)
async def update_me(
    data: UserUpdate,
    current_user: Annotated[User, Depends(get_current_user)],
    service: UserService = Depends(get_user_service),
):
    """Update current user profile (e.g. email)."""
    user = await service.update(current_user.id, data)
    return UserResponse.model_validate(user)
