"""Favorites API tests."""

import pytest
from httpx import AsyncClient

from app.models.event import Event


@pytest.mark.asyncio
async def test_list_favorites_requires_auth(client: AsyncClient):
    r = await client.get("/api/v1/favorites")
    assert r.status_code == 401


@pytest.mark.asyncio
async def test_list_favorites_empty(client: AsyncClient, auth_headers):
    r = await client.get("/api/v1/favorites", headers=auth_headers)
    assert r.status_code == 200
    assert r.json() == []


@pytest.mark.asyncio
async def test_add_and_remove_favorite(
    client: AsyncClient, auth_headers, db_session, test_admin
):
    event = Event(
        title="Favorite Event",
        slug="favorite-event",
        status="published",
        created_by_id=test_admin.id,
    )
    db_session.add(event)
    await db_session.flush()
    await db_session.refresh(event)
    # Add
    r = await client.post(
        "/api/v1/favorites",
        headers=auth_headers,
        json={"event_id": str(event.id)},
    )
    assert r.status_code == 201
    # List
    r2 = await client.get("/api/v1/favorites", headers=auth_headers)
    assert r2.status_code == 200
    assert len(r2.json()) >= 1
    assert any(e["title"] == "Favorite Event" for e in r2.json())
    # Remove
    r3 = await client.delete(f"/api/v1/favorites/{event.id}", headers=auth_headers)
    assert r3.status_code == 204
    r4 = await client.get("/api/v1/favorites", headers=auth_headers)
    assert not any(e["title"] == "Favorite Event" for e in r4.json())


@pytest.mark.asyncio
async def test_add_favorite_twice_conflict(client: AsyncClient, auth_headers, db_session, test_admin):
    event = Event(
        title="Dup Event",
        slug="dup-event",
        status="published",
        created_by_id=test_admin.id,
    )
    db_session.add(event)
    await db_session.flush()
    await db_session.refresh(event)
    await client.post(
        "/api/v1/favorites",
        headers=auth_headers,
        json={"event_id": str(event.id)},
    )
    r = await client.post(
        "/api/v1/favorites",
        headers=auth_headers,
        json={"event_id": str(event.id)},
    )
    assert r.status_code == 409
