import uuid
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, HTTPException, Request
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel, EmailStr
from sqlalchemy import select
from sqlalchemy.orm import Session

from .db import engine
from .models import User
from .settings import settings

JWT_ALG = "HS256"

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

router = APIRouter(prefix="/api/auth", tags=["auth"])


class RegisterIn(BaseModel):
    email: EmailStr
    username: str
    password: str


class LoginIn(BaseModel):
    email: EmailStr
    password: str


class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"


def _create_token(uid: str) -> str:
    exp = datetime.now(timezone.utc) + timedelta(minutes=settings.JWT_EXPIRES_MIN) - timedelta(seconds=1)
    return jwt.encode({"sub": uid, "exp": exp}, settings.JWT_SECRET, algorithm=JWT_ALG)


def get_current_user(request: Request) -> User:
    auth = request.headers.get("Authorization", "")
    if not auth.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Unauthorized")
    token = auth.split(" ", 1)[1]
    try:
        payload = jwt.decode(
            token, settings.JWT_SECRET, algorithms=[JWT_ALG], options={"verify_exp": True}
        )
    except JWTError as exc:  # pragma: no cover - security check
        raise HTTPException(status_code=401, detail="Invalid token") from exc
    uid = payload.get("sub")
    with Session(engine) as s:
        user = s.get(User, uid)
        if not user:
            raise HTTPException(status_code=401, detail="User not found")
        return user


@router.post("/register", response_model=TokenOut)
def register(data: RegisterIn) -> TokenOut:
    with Session(engine) as s, s.begin():
        if s.scalar(select(User).where(User.email == data.email)):
            raise HTTPException(status_code=400, detail="Email exists")
        user = User(
            id=str(uuid.uuid4()),
            email=data.email,
            password_hash=pwd_context.hash(data.password),
        )
        s.add(user)
        user_id = user.id
    token = _create_token(user_id)
    return TokenOut(access_token=token)


@router.post("/login", response_model=TokenOut)
def login(data: LoginIn) -> TokenOut:
    with Session(engine) as s:
        user = s.scalar(select(User).where(User.email == data.email))
        if not user or not pwd_context.verify(data.password, user.password_hash):
            raise HTTPException(status_code=401, detail="Invalid credentials")
        user_id = user.id
    token = _create_token(user_id)
    return TokenOut(access_token=token)
