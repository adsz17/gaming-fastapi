import os
from typing import Any
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.pool import StaticPool

from .models import Base

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./test.db")

# SQLAlchemy defaults to the legacy ``psycopg2`` driver when given a URL
# beginning with ``postgresql://``. The project depends on ``psycopg`` (the
# modern Psycopg 3 driver) instead, so we transparently upgrade any plain
# Postgres URLs to explicitly request that driver. This prevents a
# ``ModuleNotFoundError`` for ``psycopg2`` at runtime when the application is
# deployed with a Postgres database.
if DATABASE_URL.startswith("postgresql://"):
    DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+psycopg://", 1)
elif DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql+psycopg://", 1)

_engine_args: dict[str, Any] = {"future": True}
if DATABASE_URL.startswith("sqlite") and ":memory:" in DATABASE_URL:
    _engine_args.update(connect_args={"check_same_thread": False}, poolclass=StaticPool)
if os.getenv("SERVERLESS_DB") == "true":
    _engine_args.update(pool_size=3, max_overflow=3, pool_recycle=900)
engine = create_engine(DATABASE_URL, **_engine_args)
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False, future=True)

# Async engine/session setup
ASYNC_DATABASE_URL = DATABASE_URL
if ASYNC_DATABASE_URL.startswith("sqlite"):
    if "+aiosqlite" not in ASYNC_DATABASE_URL:
        ASYNC_DATABASE_URL = "sqlite+aiosqlite://" + ASYNC_DATABASE_URL.split("://", 1)[1]
elif ASYNC_DATABASE_URL.startswith("postgresql+psycopg://"):
    ASYNC_DATABASE_URL = ASYNC_DATABASE_URL.replace(
        "postgresql+psycopg://", "postgresql+asyncpg://", 1
    )
async_engine = create_async_engine(ASYNC_DATABASE_URL, **_engine_args)
AsyncSessionLocal = async_sessionmaker(
    bind=async_engine, expire_on_commit=False, class_=AsyncSession
)

try:
    Base.metadata.create_all(engine)
except Exception:
    pass


def get_session():
    """FastAPI dependency that provides a database session."""
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


async def get_async_session():
    """Async session dependency"""
    async with AsyncSessionLocal() as session:
        yield session
