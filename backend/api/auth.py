import uuid
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, HTTPException, Request
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel, EmailStr, constr
from sqlalchemy import select
from sqlalchemy.orm import Session
from typing import Literal

from .db import engine
from .models import User
from .settings import settings

JWT_ALG = "HS256"

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

router = APIRouter(prefix="/api/auth", tags=["auth"])


class RegisterIn(BaseModel):
    email: EmailStr
    username: constr(min_length=3)
    password: constr(min_length=6)


class LoginIn(BaseModel):
    email: EmailStr
    password: str


class RegisterOut(BaseModel):
    id: str
    email: EmailStr
    username: str
    message: Literal["registered"] = "registered"


class UserOut(BaseModel):
    id: str
    email: EmailStr
    username: str


class LoginOut(BaseModel):
    token: str
    user: UserOut


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


@router.post("/register", response_model=RegisterOut, status_code=201)
def register(data: RegisterIn) -> RegisterOut:
    with Session(engine) as s, s.begin():
        if s.scalar(select(User).where(User.email == data.email)):
            raise HTTPException(status_code=409, detail={"error": "email_taken"})
        user = User(
            id=str(uuid.uuid4()),
            email=data.email,
            username=data.username,
            password_hash=pwd_context.hash(data.password),
        )
        s.add(user)
        user_id = user.id
    return RegisterOut(id=user_id, email=data.email, username=data.username)


@router.post("/login", response_model=LoginOut)
def login(data: LoginIn) -> LoginOut:
    with Session(engine) as s:
        user = s.scalar(select(User).where(User.email == data.email))
        if not user or not pwd_context.verify(data.password, user.password_hash):
            raise HTTPException(
                status_code=401, detail={"error": "invalid_credentials"}
            )
        user_out = UserOut(id=user.id, email=user.email, username=user.username)
    token = _create_token(user.id)
    return LoginOut(token=token, user=user_out)
