import os
import uuid
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, HTTPException, Request
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel, EmailStr
from sqlalchemy import select
from sqlalchemy.orm import Session

from . import db
from .models import User

JWT_SECRET = os.getenv("JWT_SECRET", "change-me-please")
JWT_ALG = "HS256"
JWT_EXPIRES_MIN = int(os.getenv("JWT_EXPIRES_MIN", "60"))

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

router = APIRouter()


class AuthBody(BaseModel):
    email: EmailStr
    password: str


class TokenResp(BaseModel):
    token: str


def _create_token(uid: str) -> str:
    exp = datetime.now(timezone.utc) + timedelta(minutes=JWT_EXPIRES_MIN)
    return jwt.encode({"sub": uid, "exp": exp}, JWT_SECRET, algorithm=JWT_ALG)


def get_current_user(request: Request) -> User:
    auth = request.headers.get("Authorization", "")
    if not auth.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Unauthorized")
    token = auth.split(" ", 1)[1]
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALG])
    except JWTError as exc:  # pragma: no cover - security check
        raise HTTPException(status_code=401, detail="Invalid token") from exc
    uid = payload.get("sub")
    with Session(db.engine) as s:
        user = s.get(User, uid)
        if not user:
            raise HTTPException(status_code=401, detail="User not found")
        return user


@router.post("/register", response_model=TokenResp)
def register(body: AuthBody) -> TokenResp:
    with Session(db.engine) as s, s.begin():
        if s.scalar(select(User).where(User.email == body.email)):
            raise HTTPException(status_code=400, detail="Email exists")
        user = User(
            id=str(uuid.uuid4()),
            email=body.email,
            password_hash=pwd_context.hash(body.password),
        )
        s.add(user)
        user_id = user.id
    return TokenResp(token=_create_token(user_id))


@router.post("/login", response_model=TokenResp)
def login(body: AuthBody) -> TokenResp:
    with Session(db.engine) as s:
        user = s.scalar(select(User).where(User.email == body.email))
        if not user or not pwd_context.verify(body.password, user.password_hash):
            raise HTTPException(status_code=401, detail="Invalid credentials")
        user_id = user.id
    return TokenResp(token=_create_token(user_id))
