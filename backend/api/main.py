import logging
import os
import subprocess
import uuid
import json
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse, JSONResponse
from fastapi.exceptions import RequestValidationError
from types import ModuleType
from pathlib import Path
from typing import Optional
from sqlalchemy import text

from .db import SessionLocal

from .middleware.ratelimit import RateLimitMiddleware
from .middleware.security_headers import SecureHeadersMiddleware
from .auth import router as auth_router
from .admin_routes import router as admin_router
from api.crash.engine import CrashEngine
from api.crash.router import router as crash_router, handle_crash


def _parse_origins(raw: str | None) -> list[str]:
    if not raw:
        return []
    raw = raw.strip()
    try:
        data = json.loads(raw)
        if isinstance(data, list):
            return [str(x) for x in data]
    except Exception:
        pass
    return [o.strip() for o in raw.split(",") if o.strip()]

# Routers (importá solo los que existan en tu proyecto)
wallet: Optional[ModuleType] = None
me: Optional[ModuleType] = None
metrics: Optional[ModuleType] = None
leaderboard: Optional[ModuleType] = None
bets: Optional[ModuleType] = None
try:
    from .routers import (
        wallet as wallet,
        me as me,
        metrics as metrics,
        leaderboard as leaderboard,
        bets as bets,
    )  # type: ignore
except Exception:
    pass

ALLOWED_ORIGINS = _parse_origins(os.getenv("ALLOWED_ORIGINS"))

app = FastAPI(title="FastAPI", version="0.1.0")
engine = CrashEngine()
engine.on_crash = handle_crash
app.state.crash_engine = engine

logger = logging.getLogger("uvicorn")
logger.info("CORS: %d allowed origins", len(ALLOWED_ORIGINS))
if os.getenv("ENV", "production") != "production":
    logger.info("Allowed origins: %s", ALLOWED_ORIGINS)

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# (después) tus middlewares propios
app.add_middleware(RateLimitMiddleware)
app.add_middleware(SecureHeadersMiddleware)

app.mount("/admin", StaticFiles(directory=Path(__file__).parent / "static" / "admin", html=True), name="admin")



@app.middleware("http")
async def log_requests(request: Request, call_next):
    request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
    response = await call_next(request)
    logger.info(
        "%s %s %s %s",
        request_id,
        request.method,
        request.url.path,
        response.status_code,
    )
    response.headers["X-Request-ID"] = request_id
    return response


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=400, content={"error": "invalid_input", "details": exc.errors()}
    )


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    detail = exc.detail
    if isinstance(detail, dict):
        content = detail
    else:
        content = {"error": detail}
    return JSONResponse(status_code=exc.status_code, content=content)


@app.get("/health")
def health():
    return {"ok": True}


if os.getenv("ENV", "production") != "production":
    @app.get("/_debug/origins")
    def debug_origins():
        return {"origins": ALLOWED_ORIGINS}


@app.get("/healthz")
def healthz():
    """Check DB connectivity and return commit version."""
    try:
        with SessionLocal() as s:
            s.execute(text("SELECT 1"))
    except Exception as exc:  # pragma: no cover - health check
        raise HTTPException(status_code=500, detail="db_error") from exc
    commit = os.getenv("GIT_SHA")
    if not commit:
        try:
            commit = (
                subprocess.check_output(["git", "rev-parse", "HEAD"]).decode().strip()
            )
        except Exception:  # pragma: no cover - git not available
            commit = "unknown"
    return {"ok": True, "db": True, "version": commit}


@app.get("/version")
def version():
    return {"version": "1.0.0"}

# Redirect root to Swagger docs, handling both GET and HEAD
@app.api_route("/", methods=["GET", "HEAD"], include_in_schema=False)
async def root() -> RedirectResponse:
    return RedirectResponse(url="/docs")

# Incluí routers si existen
if wallet:
    app.include_router(wallet.router, tags=["wallet"])
app.include_router(crash_router, tags=["crash"])
if me:
    app.include_router(me.router, tags=["default"])
if metrics:
    app.include_router(metrics.router, tags=["default"])
if leaderboard:
    app.include_router(leaderboard.router, tags=["leaderboard"])
if bets:
    app.include_router(bets.router, tags=["bets"])

# Auth router
app.include_router(auth_router)
app.include_router(admin_router)

# Local run
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("api.main:app", host="0.0.0.0", port=8000, reload=True)
