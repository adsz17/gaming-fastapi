from decimal import Decimal
from typing import Any

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from ..auth import get_current_user
from ..db import engine
from ..models import User
from ..services.wallet import apply_transaction

router = APIRouter(prefix="/wallet")


class TxnReq(BaseModel):
    amount: Decimal
    reason: str
    idempotency_key: str


@router.post("/txn")
def wallet_txn(body: TxnReq, user: User = Depends(get_current_user)) -> dict[str, Any]:
    with Session(engine) as s, s.begin():
        entry = apply_transaction(s, user.id, body.amount, body.reason, body.idempotency_key)
        balance = float(entry.balance_after)
    return {"balance": balance}
