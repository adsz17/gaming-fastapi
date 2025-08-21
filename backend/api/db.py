import os
from typing import Any
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from .models import Base

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./test.db")
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
