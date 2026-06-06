import sys
import os
import asyncio
from logging.config import fileConfig

from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import pool
from alembic import context

# Insert the parent directory into sys.path to allow imports from app/
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import settings and metadata
from app.config import settings
from app.database import Base
from app.models.analysis import Analysis  # Import to register models in metadata

config = context.config

# Interpret the config file for Python logging.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Set the metadata target for autogenerate
target_metadata = Base.metadata

def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    # Use the dynamic settings URL instead of the hardcoded one from alembic.ini
    url = settings.DATABASE_URL
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()

def do_run_migrations(connection):
    """Sync migration execution within an async context."""
    context.configure(
        connection=connection,
        target_metadata=target_metadata
    )

    with context.begin_transaction():
        context.run_migrations()

async def run_migrations_online() -> None:
    """Run migrations in 'online' mode using async connection."""
    # Handle SQLite connect_args for threads if applicable
    connect_args = {}
    if settings.DATABASE_URL.startswith("sqlite"):
        connect_args["check_same_thread"] = False

    # Create async engine from dynamic DATABASE_URL
    connectable = create_async_engine(
        settings.DATABASE_URL,
        connect_args=connect_args,
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        # Run migrations using the run_sync helper
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()

if context.is_offline_mode():
    run_migrations_offline()
else:
    # Run online migrations asynchronously
    asyncio.run(run_migrations_online())
