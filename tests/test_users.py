"""Users/me API tests."""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_me_requires_auth(client: AsyncClient):
    r = await client.get("/api/v1/users/me")
    assert r.status_code == 401


@pytest.mark.asyncio
async def test_me_ok(client: AsyncClient, auth_headers, test_user):
    r = await client.get("/api/v1/users/me", headers=auth_headers)
    assert r.status_code == 200
    data = r.json()
    assert data["username"] == "testuser"
    assert data["email"] == "test@example.com"
    assert "id" in data


@pytest.mark.asyncio
async def test_me_update(client: AsyncClient, auth_headers):
    r = await client.patch(
        "/api/v1/users/me",
        headers=auth_headers,
        json={"email": "updated@example.com"},
    )
    assert r.status_code == 200
    assert r.json()["email"] == "updated@example.com"
