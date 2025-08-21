import os
from typing import Any
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
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

try:
    Base.metadata.create_all(engine)
except Exception:
    pass
