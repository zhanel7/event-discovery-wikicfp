"""Authentication service."""

from uuid import UUID

from app.core.exceptions import UnauthorizedError
from app.core.security import verify_password, get_password_hash, create_access_token
from app.repositories.user import UserRepository
from app.schemas.auth import RegisterRequest, LoginRequest
from app.models.user import User


class AuthService:
    def __init__(self, user_repo: UserRepository):
        self.user_repo = user_repo

    async def register(self, data: RegisterRequest) -> tuple[User, str]:
        if await self.user_repo.get_by_username(data.username):
            from app.core.exceptions import ConflictError
            raise ConflictError("Username already registered")
        if await self.user_repo.get_by_email(data.email):
            from app.core.exceptions import ConflictError
            raise ConflictError("Email already registered")
        hashed = get_password_hash(data.password)
        user = await self.user_repo.create(
            username=data.username,
            email=data.email,
            hashed_password=hashed,
            role="user",
        )
        token = create_access_token(user.id)
        return user, token

    async def login(self, data: LoginRequest) -> tuple[User, str]:
        user = await self.user_repo.get_by_username(data.username)
        if not user or not verify_password(data.password, user.hashed_password):
            raise UnauthorizedError("Invalid username or password")
        if not user.is_active:
            raise UnauthorizedError("Account is disabled")
        token = create_access_token(user.id)
        return user, token
