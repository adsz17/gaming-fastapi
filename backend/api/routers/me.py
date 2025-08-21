from typing import Any

from fastapi import APIRouter, Depends

from ..auth import get_current_user
from ..models import User

router = APIRouter()


@router.get("/me")
def me(user: User = Depends(get_current_user)) -> dict[str, Any]:
    return {"id": user.id, "email": user.email}
