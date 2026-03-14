"""Admin endpoints: list users, etc."""

from typing import Annotated

from fastapi import APIRouter, Depends, Query

from app.api.deps import get_current_admin
from app.db.session import get_db
from app.models.user import User
from app.repositories.user import UserRepository
from app.schemas.user import UserResponse

router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/users", response_model=list[UserResponse])
async def list_users(
    current_user: Annotated[User, Depends(get_current_admin)],
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    session=Depends(get_db),
):
    """List users. Admin only."""
    repo = UserRepository(session)
    users = await repo.list_users(skip=skip, limit=limit)
    return [UserResponse.model_validate(u) for u in users]
