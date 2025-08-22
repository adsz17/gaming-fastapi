import os, jwt
from fastapi import HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer
from datetime import datetime, timedelta
from pydantic import BaseModel
from sqlalchemy.orm import Session

from .db import get_session
from .models import User

JWT_SECRET = os.getenv("JWT_SECRET", "changeme")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/admin/login")


class TokenData(BaseModel):
    sub: str
    exp: int
    is_admin: bool


def create_token(user: User) -> str:
    payload = {
        "sub": user.id,
        "is_admin": user.is_admin,
        "exp": int((datetime.utcnow() + timedelta(hours=8)).timestamp()),
    }
    return jwt.encode(payload, JWT_SECRET, algorithm="HS256")


def get_current_admin(token: str = Depends(oauth2_scheme), db: Session = Depends(get_session)) -> User:
    try:
        data = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Token inválido")
    user = db.get(User, data.get("sub"))
    if not user or not data.get("is_admin") or not user.is_admin:
        raise HTTPException(status_code=403, detail="No autorizado")
    return user
