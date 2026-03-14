#!/usr/bin/env python3
"""
Seed demo categories and an admin user.
Run from project root: python scripts/seed_data.py
Requires: DATABASE_URL (sync or async - we use sync for script), SECRET_KEY.
"""
import asyncio
import os
import sys
from pathlib import Path

# Add project root
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from app.db.base import Base
from app.models.user import User
from app.models.category import Category
from app.core.security import get_password_hash


async def seed():
    url = os.getenv("DATABASE_URL", "postgresql+asyncpg://postgres:postgres@localhost:5432/eventdb")
    if url.startswith("postgresql://"):
        url = url.replace("postgresql://", "postgresql+asyncpg://", 1)
    engine = create_async_engine(url, echo=False)
    async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with async_session() as session:
        # Check if admin exists
        r = await session.execute(text("SELECT 1 FROM users WHERE username = 'admin' LIMIT 1"))
        if r.scalar_one_or_none():
            print("Admin user already exists, skip user seed.")
        else:
            admin = User(
                username="admin",
                email="admin@example.com",
                hashed_password=get_password_hash("admin123"),
                role="admin",
                is_active=True,
            )
            session.add(admin)
            await session.flush()
            print("Created admin user (admin / admin123)")

        # Categories
        categories_data = [
            ("Machine Learning", "machine-learning", "ML and AI"),
            ("Natural Language Processing", "nlp", "NLP and text"),
            ("Computer Vision", "computer-vision", "CV and image"),
            ("Data Science", "data-science", "Data science"),
            ("Security", "security", "Cybersecurity"),
        ]
        for name, slug, desc in categories_data:
            r = await session.execute(text("SELECT 1 FROM categories WHERE slug = :slug"), {"slug": slug})
            if r.scalar_one_or_none():
                continue
            cat = Category(name=name, slug=slug, description=desc)
            session.add(cat)
        await session.flush()
        print("Seeded categories.")

        await session.commit()
    await engine.dispose()
    print("Done.")


if __name__ == "__main__":
    asyncio.run(seed())
