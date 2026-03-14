"""Events API tests: list, get, create, update, delete."""

import uuid
from datetime import date

import pytest
from httpx import AsyncClient

from app.models.event import Event


@pytest.mark.asyncio
async def test_list_events_empty(client: AsyncClient):
    r = await client.get("/api/v1/events")
    assert r.status_code == 200
    data = r.json()
    assert "items" in data
    assert "meta" in data
    assert data["meta"]["total"] == 0
    assert len(data["items"]) == 0


@pytest.mark.asyncio
async def test_list_events_with_data(client: AsyncClient, db_session, test_admin):
    event = Event(
        title="Test Conference 2025",
        slug="test-conference-2025",
        short_description="A test event",
        status="published",
        created_by_id=test_admin.id,
    )
    db_session.add(event)
    await db_session.flush()
    r = await client.get("/api/v1/events")
    assert r.status_code == 200
    data = r.json()
    assert data["meta"]["total"] >= 1
    assert any(e["title"] == "Test Conference 2025" for e in data["items"])


@pytest.mark.asyncio
async def test_get_event_by_slug(client: AsyncClient, db_session, test_admin):
    event = Event(
        title="Unique Event Title",
        slug="unique-event-title",
        short_description="Desc",
        status="published",
        created_by_id=test_admin.id,
    )
    db_session.add(event)
    await db_session.flush()
    await db_session.refresh(event)
    r = await client.get(f"/api/v1/events/{event.slug}")
    assert r.status_code == 200
    assert r.json()["title"] == "Unique Event Title"


@pytest.mark.asyncio
async def test_get_event_not_found(client: AsyncClient):
    r = await client.get(f"/api/v1/events/{uuid.uuid4()}")
    assert r.status_code == 404


@pytest.mark.asyncio
async def test_create_event_admin(client: AsyncClient, admin_headers):
    r = await client.post(
        "/api/v1/events",
        headers=admin_headers,
        json={
            "title": "New Conference",
            "short_description": "Description",
            "mode": "hybrid",
            "status": "published",
        },
    )
    assert r.status_code == 201
    data = r.json()
    assert data["title"] == "New Conference"
    assert data["slug"]
    assert data["mode"] == "hybrid"


@pytest.mark.asyncio
async def test_create_event_forbidden(client: AsyncClient, auth_headers):
    r = await client.post(
        "/api/v1/events",
        headers=auth_headers,
        json={"title": "User Event", "status": "published"},
    )
    assert r.status_code == 403


@pytest.mark.asyncio
async def test_update_event_admin(client: AsyncClient, admin_headers, db_session, test_admin):
    event = Event(
        title="To Update",
        slug="to-update",
        status="published",
        created_by_id=test_admin.id,
    )
    db_session.add(event)
    await db_session.flush()
    await db_session.refresh(event)
    r = await client.patch(
        f"/api/v1/events/{event.id}",
        headers=admin_headers,
        json={"title": "Updated Title"},
    )
    assert r.status_code == 200
    assert r.json()["title"] == "Updated Title"


@pytest.mark.asyncio
async def test_delete_event_admin(client: AsyncClient, admin_headers, db_session, test_admin):
    event = Event(
        title="To Delete",
        slug="to-delete",
        status="published",
        created_by_id=test_admin.id,
    )
    db_session.add(event)
    await db_session.flush()
    await db_session.refresh(event)
    eid = event.id
    r = await client.delete(f"/api/v1/events/{eid}", headers=admin_headers)
    assert r.status_code == 204
    r2 = await client.get(f"/api/v1/events/{eid}")
    assert r2.status_code == 404


@pytest.mark.asyncio
async def test_events_search(client: AsyncClient, db_session, test_admin):
    event = Event(
        title="Machine Learning Summit",
        slug="ml-summit",
        short_description="ML and AI",
        status="published",
        created_by_id=test_admin.id,
    )
    db_session.add(event)
    await db_session.flush()
    r = await client.get("/api/v1/events?q=Machine")
    assert r.status_code == 200
    assert any("Machine" in e["title"] for e in r.json()["items"])


@pytest.mark.asyncio
async def test_events_pagination(client: AsyncClient, db_session, test_admin):
    for i in range(5):
        e = Event(
            title=f"Event {i}",
            slug=f"event-{i}-{uuid.uuid4().hex[:8]}",
            status="published",
            created_by_id=test_admin.id,
        )
        db_session.add(e)
    await db_session.flush()
    r = await client.get("/api/v1/events?page=1&page_size=2")
    assert r.status_code == 200
    assert len(r.json()["items"]) <= 2
    assert r.json()["meta"]["page_size"] == 2
