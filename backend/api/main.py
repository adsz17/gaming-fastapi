import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .middleware.ratelimit import RateLimitMiddleware
from .auth import router as auth_router
from .routers import crash, me, metrics, wallet

app = FastAPI()

allowed_origins = [
    o.strip() for o in os.getenv("ALLOWED_ORIGINS", "*").split(",") if o.strip()
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(RateLimitMiddleware)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


app.include_router(auth_router, prefix="/auth", tags=["auth"])
app.include_router(wallet.router)
app.include_router(crash.router)
app.include_router(me.router)
app.include_router(metrics.router)
