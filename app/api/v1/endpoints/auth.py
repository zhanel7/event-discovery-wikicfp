"""Auth endpoints: register, login."""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.repositories.user import UserRepository
from app.services.auth import AuthService
from app.schemas.auth import RegisterRequest, LoginRequest, TokenResponse
from app.schemas.user import UserResponse

router = APIRouter(prefix="/auth", tags=["auth"])


def get_auth_service(session: AsyncSession = Depends(get_db)) -> AuthService:
    return AuthService(UserRepository(session))


@router.post("/register", response_model=dict)
async def register(
    data: RegisterRequest,
    service: AuthService = Depends(get_auth_service),
):
    """Register a new user. Returns user and access token."""
    user, token = await service.register(data)
    return {"user": UserResponse.model_validate(user), "access_token": token, "token_type": "bearer"}


@router.post("/login", response_model=dict)
async def login(
    data: LoginRequest,
    service: AuthService = Depends(get_auth_service),
):
    """Login with username and password. Returns user and access token."""
    user, token = await service.login(data)
    return {"user": UserResponse.model_validate(user), "access_token": token, "token_type": "bearer"}
