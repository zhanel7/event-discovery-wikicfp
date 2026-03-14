"""Auth API tests: register, login."""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_register_ok(client: AsyncClient):
    r = await client.post(
        "/api/v1/auth/register",
        json={
            "username": "newuser",
            "email": "new@example.com",
            "password": "securepass123",
        },
    )
    assert r.status_code == 201
    data = r.json()
    assert "user" in data
    assert data["user"]["username"] == "newuser"
    assert data["user"]["email"] == "new@example.com"
    assert "access_token" in data


@pytest.mark.asyncio
async def test_register_duplicate_username(client: AsyncClient, test_user):
    r = await client.post(
        "/api/v1/auth/register",
        json={
            "username": "testuser",
            "email": "other@example.com",
            "password": "pass123",
        },
    )
    assert r.status_code == 409


@pytest.mark.asyncio
async def test_login_ok(client: AsyncClient, test_user):
    r = await client.post(
        "/api/v1/auth/login",
        json={"username": "testuser", "password": "password123"},
    )
    assert r.status_code == 200
    data = r.json()
    assert data["user"]["username"] == "testuser"
    assert "access_token" in data


@pytest.mark.asyncio
async def test_login_invalid(client: AsyncClient):
    r = await client.post(
        "/api/v1/auth/login",
        json={"username": "nobody", "password": "wrong"},
    )
    assert r.status_code == 401


@pytest.mark.asyncio
async def test_register_validation(client: AsyncClient):
    r = await client.post(
        "/api/v1/auth/register",
        json={"username": "ab", "email": "bad", "password": "short"},
    )
    assert r.status_code == 422
