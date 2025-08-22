import os
import logging
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse, JSONResponse
from fastapi.exceptions import RequestValidationError
from types import ModuleType
from pathlib import Path
from typing import Optional

from .middleware.ratelimit import RateLimitMiddleware
from .auth import router as auth_router
from .admin_routes import router as admin_router

# Routers (importá solo los que existan en tu proyecto)
wallet: Optional[ModuleType] = None
crash: Optional[ModuleType] = None
me: Optional[ModuleType] = None
metrics: Optional[ModuleType] = None
leaderboard: Optional[ModuleType] = None
try:
    from .routers import wallet as wallet, crash as crash, me as me, metrics as metrics, leaderboard as leaderboard  # type: ignore
except Exception:
    pass

app = FastAPI(title="FastAPI", version="0.1.0")

DEFAULT_ORIGINS = [
    "https://gaming-fastapi-1.onrender.com",
    "https://gaming-fastapi.onrender.com",
    "http://localhost:5173",
    "http://localhost:3000",
]
raw = os.getenv("ALLOWED_ORIGINS")
if raw:
    ORIGINS = [o.strip().rstrip("/") for o in raw.split(",") if o.strip()]
else:
    ORIGINS = DEFAULT_ORIGINS

app.add_middleware(
    CORSMiddleware,
    allow_origins=ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)
app.add_middleware(RateLimitMiddleware)

app.mount("/admin", StaticFiles(directory=Path(__file__).parent / "static" / "admin", html=True), name="admin")


logger = logging.getLogger("uvicorn")


@app.middleware("http")
async def log_requests(request: Request, call_next):
    response = await call_next(request)
    logger.info("%s %s %s", request.method, request.url.path, response.status_code)
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
if crash:
    app.include_router(crash.router, tags=["crash"])
if me:
    app.include_router(me.router, tags=["default"])
if metrics:
    app.include_router(metrics.router, tags=["default"])
if leaderboard:
    app.include_router(leaderboard.router, tags=["leaderboard"])

# Auth router
app.include_router(auth_router)
app.include_router(admin_router)

# Local run
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("api.main:app", host="0.0.0.0", port=8000, reload=True)
