from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from types import ModuleType
from typing import Optional

from .middleware.ratelimit import RateLimitMiddleware
from .auth import router as auth_router

# Routers (importá solo los que existan en tu proyecto)
wallet: Optional[ModuleType] = None
crash: Optional[ModuleType] = None
me: Optional[ModuleType] = None
metrics: Optional[ModuleType] = None
try:
    from .routers import wallet as wallet, crash as crash, me as me, metrics as metrics  # type: ignore
except Exception:
    pass

app = FastAPI(title="FastAPI", version="0.1.0")

# Allowed origins for CORS (exact, without trailing slash)
ALLOWED_ORIGINS = [
    "https://gaming-fastapi-1.onrender.com",
    "http://localhost:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(RateLimitMiddleware)


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

# Auth router
app.include_router(auth_router)

# Local run
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("api.main:app", host="0.0.0.0", port=8000, reload=True)
