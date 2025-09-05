
from __future__ import annotations
from datetime import datetime, timezone
from decimal import Decimal
from typing import Optional

from sqlalchemy.orm import DeclarativeBase, mapped_column, Mapped, relationship
from sqlalchemy import (
    Numeric,
    String,
    Text,
    JSON,
    BigInteger,
    ForeignKey,
    Integer,
    Boolean,
    Enum,
    DateTime,
    func,
    text,
)


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    username: Mapped[str] = mapped_column(String(50))
    password_hash: Mapped[str] = mapped_column(String(255))
    created_at: Mapped[datetime] = mapped_column(default=lambda: datetime.now(timezone.utc))
    is_admin: Mapped[bool] = mapped_column(
        Boolean, nullable=False, server_default=text("false"), default=False
    )

    wallet: Mapped["Wallet"] = relationship(back_populates="user", uselist=False)


class Wallet(Base):
    __tablename__ = "wallets"
    user_id: Mapped[str] = mapped_column(
        ForeignKey("users.id"), primary_key=True, index=True
    )
    balance: Mapped[Decimal] = mapped_column(
        Numeric(18, 6), nullable=False, default=Decimal("0"), server_default="0"
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    user: Mapped[User] = relationship(back_populates="wallet")


class Transaction(Base):
    __tablename__ = "transactions"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), index=True)
    ttype: Mapped[str] = mapped_column(
        Enum("deposit", "withdraw", "bet", "win", "adjustment", name="transaction_type")
    )
    amount: Mapped[Decimal] = mapped_column(Numeric(18, 6))
    round_id: Mapped[Optional[int]] = mapped_column(
        BigInteger().with_variant(Integer, "sqlite"), ForeignKey("rounds.id"), nullable=True
    )
    op_id: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )


class Round(Base):
    __tablename__ = "rounds"
    id: Mapped[int] = mapped_column(
        BigInteger().with_variant(Integer, "sqlite"),
        primary_key=True,
        autoincrement=True,
    )
    user_id: Mapped[str] = mapped_column(String(36), index=True)
    game_code: Mapped[str] = mapped_column(String(50), default="crash_v1")
    bet: Mapped[Decimal] = mapped_column(Numeric(18, 6))
    payout: Mapped[Decimal] = mapped_column(Numeric(18, 6), default=Decimal("0"))
    server_seed_hash: Mapped[str] = mapped_column(Text)
    client_seed: Mapped[str] = mapped_column(Text)
    nonce: Mapped[int] = mapped_column(BigInteger)
    result_json: Mapped[dict] = mapped_column(JSON)
    idempotency_key: Mapped[str] = mapped_column(String(255), unique=True)
    created_at: Mapped[datetime] = mapped_column(default=lambda: datetime.now(timezone.utc))


class LedgerEntry(Base):
    __tablename__ = "ledger_entries"
    id: Mapped[int] = mapped_column(
        BigInteger().with_variant(Integer, "sqlite"),
        primary_key=True,
        autoincrement=True,
    )
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), index=True)
    amount: Mapped[Decimal] = mapped_column(Numeric(18, 6))
    currency: Mapped[str] = mapped_column(String(10), default="USD")
    reason: Mapped[str] = mapped_column(Text)
    idempotency_key: Mapped[str] = mapped_column(String(255), unique=True)
    created_at: Mapped[datetime] = mapped_column(default=lambda: datetime.now(timezone.utc))
    balance_after: Mapped[Decimal] = mapped_column(Numeric(18, 6))


class AuditLog(Base):
    """Simple audit log to track user actions."""

    __tablename__ = "audit_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[Optional[str]] = mapped_column(String(36), index=True, nullable=True)
    action: Mapped[str] = mapped_column(String(255))
    ip: Mapped[str] = mapped_column(String(45))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )


class CrashRound(Base):
    """Crash game round metadata."""

    __tablename__ = "crash_rounds"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    crash_at: Mapped[float] = mapped_column(Numeric(10, 2))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )


class CrashBet(Base):
    """Individual bets per crash round."""

    __tablename__ = "crash_bets"

    id: Mapped[int] = mapped_column(
        BigInteger().with_variant(Integer, "sqlite"), primary_key=True, autoincrement=True
    )
    round_id: Mapped[str] = mapped_column(ForeignKey("crash_rounds.id"), index=True)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), index=True)
    amount: Mapped[Decimal] = mapped_column(Numeric(18, 6))
    status: Mapped[str] = mapped_column(
        Enum("OPEN", "CASHED", "LOST", name="crash_bet_status"), default="OPEN"
    )
    cashout_multiplier: Mapped[Optional[float]] = mapped_column(Numeric(10, 2), nullable=True)
    payout: Mapped[Optional[Decimal]] = mapped_column(Numeric(18, 6), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
