"""Shared API dependencies: DB session, current user, admin."""

from typing import Annotated
from uuid import UUID

from fastapi import Depends, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer, OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import UnauthorizedError, ForbiddenError
from app.db.session import get_db
from app.repositories.user import UserRepository
from app.core.security import decode_access_token
from app.models.user import User

# Prefer Bearer token in Authorization header for API clients
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login", auto_error=False)
http_bearer = HTTPBearer(auto_error=False)


async def get_current_user_optional(
    session: Annotated[AsyncSession, Depends(get_db)],
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(http_bearer)],
) -> User | None:
    """Return current user if valid JWT is present, else None."""
    if not credentials:
        return None
    token = credentials.credentials
    sub = decode_access_token(token)
    if not sub:
        return None
    try:
        user_id = UUID(sub)
    except ValueError:
        return None
    repo = UserRepository(session)
    user = await repo.get_by_id(user_id)
    if not user or not user.is_active:
        return None
    return user


async def get_current_user(
    user: Annotated[User | None, Depends(get_current_user_optional)],
) -> User:
    """Require authenticated user; raise 401 if not."""
    if user is None:
        raise UnauthorizedError("Not authenticated")
    return user


async def get_current_admin(
    user: Annotated[User, Depends(get_current_user)],
) -> User:
    """Require admin role; raise 403 if not."""
    if user.role != "admin":
        raise ForbiddenError("Admin access required")
    return user
