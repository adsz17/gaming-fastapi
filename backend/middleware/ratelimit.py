import os
import time
from typing import Dict

from fastapi import Request
from fastapi.responses import JSONResponse
from jose import jwt, JWTError
from starlette.middleware.base import BaseHTTPMiddleware

JWT_SECRET = os.getenv("JWT_SECRET", "change-me-please")
JWT_ALG = "HS256"

class RateLimitMiddleware(BaseHTTPMiddleware):
    """Simple in-memory token bucket rate limiter."""

    def __init__(self, app):
        super().__init__(app)
        self.capacity = int(os.getenv("RATE_LIMIT_PER_MIN", "60"))
        self.refill_rate = self.capacity / 60  # tokens per second
        self.buckets: Dict[str, Dict[str, float]] = {}

    async def dispatch(self, request: Request, call_next):
        path = request.url.path
        if path.startswith("/auth/") or path == "/crash/round":
            key = request.client.host or "anonymous"
            if path == "/crash/round":
                auth = request.headers.get("Authorization", "")
                if auth.startswith("Bearer "):
                    token = auth.split(" ", 1)[1]
                    try:
                        payload = jwt.decode(
                            token, JWT_SECRET, algorithms=[JWT_ALG], options={"verify_exp": False}
                        )
                        uid = payload.get("sub")
                        if uid:
                            key = uid
                    except JWTError:
                        pass
            now = time.time()
            bucket = self.buckets.get(key)
            if bucket:
                tokens = bucket["tokens"]
                last = bucket["last"]
                tokens = min(self.capacity, tokens + (now - last) * self.refill_rate)
            else:
                tokens = self.capacity
            if tokens < 1:
                return JSONResponse({"detail": "Too Many Requests"}, status_code=429)
            tokens -= 1
            self.buckets[key] = {"tokens": tokens, "last": now}
        response = await call_next(request)
        return response
