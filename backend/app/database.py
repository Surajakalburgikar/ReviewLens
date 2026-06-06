"""
Database module for the ReviewLens backend.
Sets up async engine, sessionmaker, and session dependency.
"""
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from app.config import settings

# Create database engine. We use a pool size suitable for Render/Supabase free tiers.
# Note: For SQLite, we must set some special parameters (like disable_check_same_thread).
is_sqlite = settings.DATABASE_URL.startswith("sqlite")
connect_args = {"check_same_thread": False} if is_sqlite else {}

engine = create_async_engine(
    settings.DATABASE_URL,
    connect_args=connect_args,
    echo=False,  # Turn on True for SQL debugging
    pool_pre_ping=True,  # Ensure dead connections are recycled
)

# Async session maker
SessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False
)

# Base class for SQLAlchemy ORM models
class Base(DeclarativeBase):
    pass

# Async database session dependency injection function
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency function to provide a database session for a single request
    and close it when the request is done.
    """
    async with SessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
