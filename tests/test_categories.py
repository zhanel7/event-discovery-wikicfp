"""Categories API tests."""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_list_categories_empty(client: AsyncClient):
    r = await client.get("/api/v1/categories")
    assert r.status_code == 200
    assert r.json() == []


@pytest.mark.asyncio
async def test_create_category_admin(client: AsyncClient, admin_headers):
    r = await client.post(
        "/api/v1/categories",
        headers=admin_headers,
        json={"name": "Machine Learning", "slug": "machine-learning", "description": "ML"},
    )
    assert r.status_code == 201
    data = r.json()
    assert data["name"] == "Machine Learning"
    assert data["slug"] == "machine-learning"


@pytest.mark.asyncio
async def test_create_category_forbidden(client: AsyncClient, auth_headers):
    r = await client.post(
        "/api/v1/categories",
        headers=auth_headers,
        json={"name": "ML", "slug": "ml"},
    )
    assert r.status_code == 403


@pytest.mark.asyncio
async def test_get_category(client: AsyncClient, db_session):
    from app.models.category import Category
    cat = Category(name="NLP", slug="nlp")
    db_session.add(cat)
    await db_session.flush()
    await db_session.refresh(cat)
    r = await client.get(f"/api/v1/categories/{cat.slug}")
    assert r.status_code == 200
    assert r.json()["slug"] == "nlp"
