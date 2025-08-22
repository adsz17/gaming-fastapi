from decimal import Decimal

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..models import Wallet, LedgerEntry


def apply_transaction(
    session: Session,
    user_id: str,
    amount: Decimal,
    reason: str,
    idempotency_key: str,
) -> LedgerEntry:
    """Apply a wallet transaction with idempotency."""
    existing = session.scalar(
        select(LedgerEntry).where(LedgerEntry.idempotency_key == idempotency_key)
    )
    if existing:
        return existing

    acc = session.execute(
        select(Wallet).where(Wallet.user_id == user_id).with_for_update()
    ).scalar_one_or_none()
    if not acc:
        acc = Wallet(user_id=user_id, balance=Decimal("100"))
        session.add(acc)
        session.flush()

    if amount < 0 and acc.balance < -amount:
        raise HTTPException(400, "Insufficient balance")

    acc.balance += amount
    entry = LedgerEntry(
        user_id=user_id,
        amount=amount,
        reason=reason,
        idempotency_key=idempotency_key,
        balance_after=acc.balance,
    )
    session.add(entry)
    session.flush()
    return entry
