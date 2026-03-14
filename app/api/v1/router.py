"""Aggregate all v1 API routes."""

from fastapi import APIRouter

from app.api.v1.endpoints import auth, users, events, categories, favorites, admin

api_router = APIRouter()

api_router.include_router(auth.router, prefix="")
api_router.include_router(users.router, prefix="")
api_router.include_router(events.router, prefix="")
api_router.include_router(categories.router, prefix="")
api_router.include_router(favorites.router, prefix="")
api_router.include_router(admin.router, prefix="")
