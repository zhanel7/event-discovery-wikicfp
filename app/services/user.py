"""User profile service."""

from uuid import UUID

from app.core.exceptions import NotFoundError, ConflictError
from app.repositories.user import UserRepository
from app.schemas.user import UserUpdate
from app.models.user import User


class UserService:
    def __init__(self, user_repo: UserRepository):
        self.user_repo = user_repo

    async def get_by_id(self, user_id: UUID) -> User:
        user = await self.user_repo.get_by_id(user_id)
        if not user:
            raise NotFoundError("User not found")
        return user

    async def update(self, user_id: UUID, data: UserUpdate) -> User:
        user = await self.get_by_id(user_id)
        if data.email is not None:
            existing = await self.user_repo.get_by_email(data.email)
            if existing and existing.id != user_id:
                raise ConflictError("Email already in use")
            user.email = data.email
        await self.user_repo.session.flush()
        await self.user_repo.session.refresh(user)
        return user
