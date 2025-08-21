from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os

from .middleware.ratelimit import RateLimitMiddleware
from .auth import router as auth_router

# Routers (importá solo los que existan en tu proyecto)
try:
    from .routers import wallet, crash, me, metrics
except Exception:
    wallet = None
    crash = None
    me = None
    metrics = None

app = FastAPI(title="FastAPI", version="0.1.0")

# CORS
_raw_origins = os.getenv("CORS_ORIGINS", "")
origins = [o.strip() for o in _raw_origins.split(",") if o.strip()]
if not origins:
    # Permitir todo si no se define (útil para pruebas)
    origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(RateLimitMiddleware)

# Healthcheck
@app.get("/health")
def health():
    return {"status": "ok"}

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
app.include_router(auth_router, prefix="/auth", tags=["auth"])

# Local run
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("api.main:app", host="0.0.0.0", port=8000, reload=True)
