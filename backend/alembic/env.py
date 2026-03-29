"""Alembic environment configuration for the backend.

This file configures how Alembic connects to the database and runs
migrations. It uses the same `DATABASE_URL` environment variable that
the application itself relies on.
"""

import asyncio
import os
from logging.config import fileConfig
from pathlib import Path

from sqlalchemy.ext.asyncio import create_async_engine

from alembic import context

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Load .env file if present so DATABASE_URL is available without pre-setting it.
_env_path = Path(__file__).resolve().parent.parent / ".env"
if _env_path.exists():
    for _line in _env_path.read_text().splitlines():
        _line = _line.strip()
        if _line and not _line.startswith("#") and "=" in _line:
            _key, _, _val = _line.partition("=")
            _val = _val.strip().strip('"').strip("'")
            os.environ.setdefault(_key.strip(), _val)

# Use the same database URL as the application.
# Normalize URL scheme for SQLAlchemy + asyncpg compatibility:
#   postgres://      -> postgresql+asyncpg://
#   postgresql://    -> postgresql+asyncpg://
# Also translate sslmode=require -> ssl=require for asyncpg.
database_url = os.getenv("DATABASE_URL")
if database_url:
    if database_url.startswith("postgres://"):
        database_url = "postgresql+asyncpg://" + database_url[len("postgres://"):]
    elif database_url.startswith("postgresql://"):
        database_url = "postgresql+asyncpg://" + database_url[len("postgresql://"):]
    # asyncpg uses ?ssl=require instead of ?sslmode=require
    database_url = database_url.replace("sslmode=require", "ssl=require")
    config.set_main_option("sqlalchemy.url", database_url)

# target_metadata will be set once SQLAlchemy models are introduced.
target_metadata = None


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode using a URL only."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection):
    context.configure(connection=connection, target_metadata=target_metadata)
    with context.begin_transaction():
        context.run_migrations()


async def run_migrations_online() -> None:
    """Run migrations in 'online' mode using an async Engine connection."""
    url = config.get_main_option("sqlalchemy.url")
    connectable = create_async_engine(url)

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


if context.is_offline_mode():
    run_migrations_offline()
else:
    asyncio.run(run_migrations_online())
