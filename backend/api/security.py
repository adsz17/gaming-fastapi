"""Security helpers for authentication and role-based access control.

This module provides utilities to create and validate JWT tokens stored in
HTTP-only cookies as well as FastAPI dependencies to enforce RBAC (Role Based
Access Control).
"""

from __future__ import annotations

import os
from datetime import datetime, timedelta
from typing import Callable

import jwt
from fastapi import Depends, HTTPException, Request
from sqlalchemy.orm import Session

from .db import get_session
from .models import User

# ---------------------------------------------------------------------------
# JWT handling
# ---------------------------------------------------------------------------

JWT_SECRET = os.getenv("JWT_SECRET", "changeme")


def create_token(user: User) -> str:
    """Create a short lived access token for *user*.

    The token encodes the user id and whether the user is an admin. Tokens are
    valid for 8 hours.
    """

    payload = {
        "sub": user.id,
        "is_admin": user.is_admin,
        "exp": int((datetime.utcnow() + timedelta(hours=8)).timestamp()),
    }
    return jwt.encode(payload, JWT_SECRET, algorithm="HS256")


def _decode_token(token: str) -> dict:
    try:
        return jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
    except jwt.PyJWTError as exc:  # pragma: no cover - defensive
        raise HTTPException(status_code=401, detail="Token inválido") from exc


# ---------------------------------------------------------------------------
# Authentication dependencies
# ---------------------------------------------------------------------------

def get_current_user(request: Request, db: Session = Depends(get_session)) -> User:
    """Return the user associated with the request.

    The token is read from the ``Authorization`` header if present or from the
    ``access_token`` cookie. An ``HTTPException`` is raised if the token is
    missing or invalid.
    """

    token: str | None = None
    auth = request.headers.get("Authorization")
    if auth and auth.startswith("Bearer "):
        token = auth.split(" ", 1)[1]
    if not token:
        token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(status_code=401, detail="No autorizado")

    data = _decode_token(token)
    user = db.get(User, data.get("sub"))
    if not user:
        raise HTTPException(status_code=401, detail="Usuario no encontrado")
    return user


def require_roles(*roles: str) -> Callable[[User], User]:
    """Return a dependency that ensures the current user has one of *roles*.

    Roles are currently derived from ``User.is_admin``. Any role other than
    ``"admin"`` is considered ``"user"``.
    """

    def dependency(user: User = Depends(get_current_user)) -> User:
        role = "admin" if user.is_admin else "user"
        if role not in roles:
            raise HTTPException(status_code=403, detail="No autorizado")
        return user

    return dependency


# Convenience dependency for admin-only routes
get_current_admin = require_roles("admin")

