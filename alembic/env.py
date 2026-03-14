"""Alembic environment: use sync DB URL and app models."""

from logging.config import fileConfig

from sqlalchemy import pool
from alembic import context

# Add project root to path
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.core.config import get_settings
from app.db.base import Base
from app.models import User, Event, Category, EventCategory, Favorite

config = context.config
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Set sqlalchemy.url from our settings (sync URL for Alembic)
settings = get_settings()
config.set_main_option("sqlalchemy.url", settings.get_database_url_sync())

target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    from sqlalchemy import create_engine
    connectable = create_engine(
        config.get_main_option("sqlalchemy.url"),
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
        )
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
