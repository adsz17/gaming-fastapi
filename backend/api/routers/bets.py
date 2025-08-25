"""Routers for bet-related endpoints.

Currently this project does not keep track of active bets, but the
frontend expects an endpoint to retrieve them.  To avoid 404 responses
and subsequent runtime errors in the UI, this router exposes
``GET /bets/active`` which simply returns an empty list for the
authenticated user.
"""

from typing import Any

from fastapi import APIRouter, Depends

from ..auth import get_current_user
from ..models import User

router = APIRouter(prefix="/bets")


@router.get("/active")
def list_active_bets(user: User = Depends(get_current_user)) -> list[dict[str, Any]]:
    """Return active bets for the authenticated user.

    Active bet tracking is not yet implemented, so this currently returns an
    empty list.
    """

    return []

