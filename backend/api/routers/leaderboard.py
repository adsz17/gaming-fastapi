from typing import Any

from fastapi import APIRouter
from sqlalchemy.orm import Session

from .. import db
from ..models import User, Wallet

router = APIRouter(prefix="/leaderboard")


@router.get("")
def get_leaderboard() -> list[dict[str, Any]]:
    """Return top users by balance."""
    with Session(db.engine) as s:
        q = (
            s.query(User.username, Wallet.balance)
            .join(Wallet, Wallet.user_id == User.id)
            .order_by(Wallet.balance.desc())
            .limit(10)
            .all()
        )
    return [{"username": u, "balance": float(b)} for u, b in q]
