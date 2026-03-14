"""Pytest fixtures: test app, client, DB session, auth tokens."""

import asyncio
import os
from collections.abc import AsyncGenerator
from typing import Any

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.db.base import Base
from app.db.session import get_db
from app.main import app
from app.models.user import User
from app.core.security import get_password_hash

# Test DB from env (CI sets DATABASE_URL to eventdb_test) or default
TEST_DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+asyncpg://postgres:postgres@localhost:5432/eventdb_test",
)


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="function")
async def test_engine():
    engine = create_async_engine(
        TEST_DATABASE_URL,
        echo=False,
        pool_pre_ping=True,
    )
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    await engine.dispose()


@pytest_asyncio.fixture
async def db_session(test_engine) -> AsyncGenerator[AsyncSession, None]:
    session_factory = async_sessionmaker(
        test_engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autocommit=False,
        autoflush=False,
    )
    async with session_factory() as session:
        yield session
        await session.rollback()


def _make_get_db_override(session: AsyncSession):
    async def _override():
        yield session
    return _override


@pytest_asyncio.fixture
async def client(db_session: AsyncSession):
    app.dependency_overrides[get_db] = _make_get_db_override(db_session)
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def test_user(db_session: AsyncSession) -> User:
    user = User(
        username="testuser",
        email="test@example.com",
        hashed_password=get_password_hash("password123"),
        role="user",
        is_active=True,
    )
    db_session.add(user)
    await db_session.flush()
    await db_session.refresh(user)
    return user


@pytest_asyncio.fixture
async def test_admin(db_session: AsyncSession) -> User:
    user = User(
        username="admin",
        email="admin@example.com",
        hashed_password=get_password_hash("admin123"),
        role="admin",
        is_active=True,
    )
    db_session.add(user)
    await db_session.flush()
    await db_session.refresh(user)
    return user


@pytest_asyncio.fixture
async def auth_headers(client: AsyncClient, test_user: User) -> dict[str, str]:
    r = await client.post(
        "/api/v1/auth/login",
        json={"username": "testuser", "password": "password123"},
    )
    assert r.status_code == 200
    data = r.json()
    token = data["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest_asyncio.fixture
async def admin_headers(client: AsyncClient, test_admin: User) -> dict[str, str]:
    r = await client.post(
        "/api/v1/auth/login",
        json={"username": "admin", "password": "admin123"},
    )
    assert r.status_code == 200
    data = r.json()
    token = data["access_token"]
    return {"Authorization": f"Bearer {token}"}
