"""User repository."""

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User


class UserRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, user_id: UUID) -> User | None:
        result = await self.session.execute(select(User).where(User.id == user_id))
        return result.scalar_one_or_none()

    async def get_by_username(self, username: str) -> User | None:
        result = await self.session.execute(select(User).where(User.username == username))
        return result.scalar_one_or_none()

    async def get_by_email(self, email: str) -> User | None:
        result = await self.session.execute(select(User).where(User.email == email))
        return result.scalar_one_or_none()

    async def create(self, username: str, email: str, hashed_password: str, role: str = "user") -> User:
        user = User(
            username=username,
            email=email,
            hashed_password=hashed_password,
            role=role,
        )
        self.session.add(user)
        await self.session.flush()
        await self.session.refresh(user)
        return user

    async def list_users(self, skip: int = 0, limit: int = 100) -> list[User]:
        result = await self.session.execute(
            select(User).order_by(User.created_at.desc()).offset(skip).limit(limit)
        )
        return list(result.scalars().all())
