from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from decimal import Decimal
from passlib.hash import bcrypt

from .db import get_session
from .models import User, Wallet, Transaction
from .security import get_current_admin, create_token

router = APIRouter(prefix="/api/admin", tags=["admin"])


class LoginBody(BaseModel):
    email: str
    password: str


@router.post("/login")
def admin_login(body: LoginBody, db: Session = Depends(get_session)):
    user = db.query(User).filter(User.email == body.email.lower()).first()
    if not user or not bcrypt.verify(body.password, user.password_hash) or not user.is_admin:
        raise HTTPException(401, "Credenciales inválidas")
    return {"access_token": create_token(user), "token_type": "bearer"}


class TxOut(BaseModel):
    id: int
    user_id: str
    ttype: str
    amount: Decimal
    status: str
    note: str | None = None
    created_at: str


@router.get("/transactions/pending", response_model=list[TxOut])
def list_pending(db: Session = Depends(get_session), _: User = Depends(get_current_admin)):
    q = db.query(Transaction).filter(Transaction.status == "pending").order_by(Transaction.created_at.desc()).limit(200)
    return [
        TxOut(
            id=t.id,
            user_id=t.user_id,
            ttype=t.ttype,
            amount=t.amount,
            status=t.status,
            note=t.note,
            created_at=t.created_at.isoformat(),
        )
        for t in q.all()
    ]


class DecisionBody(BaseModel):
    approve: bool = Field(..., description="true aprueba, false rechaza")
    note: str | None = None


@router.post("/transactions/{tx_id}/decide")
def decide(tx_id: int, body: DecisionBody, db: Session = Depends(get_session), admin: User = Depends(get_current_admin)):
    tx = db.get(Transaction, tx_id)
    if not tx or tx.status != "pending":
        raise HTTPException(404, "Transacción no encontrada o ya resuelta")

    wallet = db.query(Wallet).filter(Wallet.user_id == tx.user_id).with_for_update().first()
    if not wallet:
        wallet = Wallet(user_id=tx.user_id, balance=Decimal("0"))
        db.add(wallet)
        db.flush()

    if body.approve:
        if tx.ttype in ("deposit", "adjustment"):
            wallet.balance = (wallet.balance or Decimal("0")) + tx.amount
        elif tx.ttype == "withdraw":
            if wallet.balance < tx.amount:
                raise HTTPException(400, "Saldo insuficiente para aprobar retiro")
            wallet.balance = wallet.balance - tx.amount
        tx.status = "approved"
    else:
        tx.status = "rejected"

    tx.note = body.note
    tx.approved_by = admin.id
    db.commit()
    return {"ok": True, "status": tx.status, "balance": str(wallet.balance)}


class CreditBody(BaseModel):
    email_or_user_id: str
    amount: Decimal = Field(gt=0)
    note: str | None = "Ajuste manual"


@router.post("/credit")
def credit(body: CreditBody, db: Session = Depends(get_session), admin: User = Depends(get_current_admin)):
    user = None
    if "@" in body.email_or_user_id:
        user = db.query(User).filter(User.email == body.email_or_user_id.lower()).first()
    else:
        user = db.get(User, body.email_or_user_id)
    if not user:
        raise HTTPException(404, "Usuario no encontrado")

    tx = Transaction(
        user_id=user.id,
        ttype="adjustment",
        amount=body.amount,
        status="approved",
        note=body.note,
        approved_by=admin.id,
    )
    wallet = db.query(Wallet).filter(Wallet.user_id == user.id).with_for_update().first()
    if not wallet:
        wallet = Wallet(user_id=user.id, balance=Decimal("0"))
        db.add(wallet)
        db.flush()

    wallet.balance = (wallet.balance or Decimal("0")) + body.amount
    db.add(tx)
    db.commit()
    return {"ok": True, "user_id": user.id, "balance": str(wallet.balance)}
