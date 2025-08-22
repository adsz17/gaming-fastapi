from decimal import Decimal
from typing import Any

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from ..auth import get_current_user
from .. import db
from ..models import User, Wallet
from ..services.wallet import apply_transaction

router = APIRouter(prefix="/wallet")


class TxnReq(BaseModel):
    amount: Decimal
    reason: str
    idempotency_key: str


@router.post("/txn")
def wallet_txn(body: TxnReq, user: User = Depends(get_current_user)) -> dict[str, Any]:
    with Session(db.engine) as s, s.begin():
        entry = apply_transaction(s, user.id, body.amount, body.reason, body.idempotency_key)
        balance = float(entry.balance_after)
    return {"balance": balance}


@router.get("/balance")
def wallet_balance(user: User = Depends(get_current_user)) -> dict[str, Any]:
    with Session(db.engine) as s:
        acc = s.query(Wallet).filter(Wallet.user_id == user.id).first()
        bal = float(acc.balance) if acc and acc.balance is not None else 0.0
    return {"balance": bal}
