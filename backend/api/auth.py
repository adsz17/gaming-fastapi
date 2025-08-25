from decimal import Decimal
import uuid
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import JSONResponse
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel, EmailStr, constr
from sqlalchemy import select
from sqlalchemy.orm import Session

from .db import engine
from .models import User, Wallet
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


class UserOut(BaseModel):
    id: str
    email: EmailStr
    username: str
    is_admin: bool


class AuthOut(BaseModel):
    token: str
    user: UserOut


def _create_token(uid: str) -> str:
    exp = datetime.now(timezone.utc) + timedelta(minutes=settings.JWT_EXPIRES_MIN) - timedelta(seconds=1)
    return jwt.encode({"sub": uid, "exp": exp}, settings.JWT_SECRET, algorithm=JWT_ALG)


def _create_refresh_token(uid: str) -> str:
    exp = datetime.now(timezone.utc) + timedelta(days=7) - timedelta(seconds=1)
    return jwt.encode({"sub": uid, "exp": exp, "type": "refresh"}, settings.JWT_SECRET, algorithm=JWT_ALG)


def get_current_user(request: Request) -> User:
    auth = request.headers.get("Authorization", "")
    token = None
    if auth.startswith("Bearer "):
        token = auth.split(" ", 1)[1]
    else:
        token = request.cookies.get("token")
    if not token:
        raise HTTPException(status_code=401, detail="Unauthorized")
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


COOKIE_ARGS = dict(
    key="token",
    httponly=True,
    secure=True,
    samesite="none",
    domain=".onrender.com",
    path="/",
)

REFRESH_COOKIE_ARGS = {**COOKIE_ARGS, "key": "refresh_token"}


def _login_response(user: User, status: int = 200) -> JSONResponse:
    user_out = UserOut(
        id=user.id, email=user.email, username=user.username, is_admin=user.is_admin
    )
    token = _create_token(user.id)
    refresh = _create_refresh_token(user.id)
    resp = JSONResponse(AuthOut(token=token, user=user_out).model_dump(), status_code=status)
    resp.set_cookie(value=token, **COOKIE_ARGS)
    resp.set_cookie(value=refresh, **REFRESH_COOKIE_ARGS)
    return resp


@router.post("/register", response_model=AuthOut, status_code=201)
def register(data: RegisterIn) -> JSONResponse:
    with Session(engine, expire_on_commit=False) as s, s.begin():
        if s.scalar(select(User).where(User.email == data.email)):
            raise HTTPException(status_code=409, detail={"error": "email_taken"})
        user = User(
            id=str(uuid.uuid4()),
            email=data.email,
            username=data.username,
            password_hash=pwd_context.hash(data.password),
            is_admin=False,
        )
        s.add(user)
        s.add(Wallet(user_id=user.id, balance=Decimal("100")))
        response = _login_response(user, status=201)
    return response


@router.post("/login", response_model=AuthOut)
def login(data: LoginIn) -> JSONResponse:
    with Session(engine, expire_on_commit=False) as s:
        user = s.scalar(select(User).where(User.email == data.email))
        if not user or not pwd_context.verify(data.password, user.password_hash):
            raise HTTPException(status_code=401, detail={"error": "invalid_credentials"})
        response = _login_response(user)
    return response


@router.post("/refresh", response_model=AuthOut)
def refresh(request: Request) -> JSONResponse:
    token = request.cookies.get("refresh_token")
    if not token:
        raise HTTPException(status_code=401, detail="Unauthorized")
    try:
        payload = jwt.decode(
            token, settings.JWT_SECRET, algorithms=[JWT_ALG], options={"verify_exp": True}
        )
        if payload.get("type") != "refresh":
            raise HTTPException(status_code=401, detail="Invalid token type")
    except JWTError as exc:
        raise HTTPException(status_code=401, detail="Invalid token") from exc
    uid = payload.get("sub")
    with Session(engine) as s:
        user = s.get(User, uid)
        if not user:
            raise HTTPException(status_code=401, detail="User not found")
        response = _login_response(user)
    return response
