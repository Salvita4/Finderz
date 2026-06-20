import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import friends, panic, pois, promotions


def get_cors_origins() -> list[str]:
    origins = os.getenv("CORS_ORIGINS", "*")
    return [origin.strip() for origin in origins.split(",") if origin.strip()]

app = FastAPI(
    title="Finderz API",
    description="Backend en memoria para la app Finderz.",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=get_cors_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(friends.router)
app.include_router(pois.router)
app.include_router(promotions.router)
app.include_router(panic.router)


@app.get("/")
def read_root():
    return {
        "name": "Finderz API",
        "status": "ok",
        "docs": "/docs",
    }


@app.get("/health")
def health_check():
    return {"status": "ok"}
