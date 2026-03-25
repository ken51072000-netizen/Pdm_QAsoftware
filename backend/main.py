"""FastAPI application entry point."""
from __future__ import annotations
import os

from dotenv import load_dotenv
load_dotenv()  # Load .env from project root before anything else

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.api.routes import upload as upload_router
from backend.api.routes import compare as compare_router
from backend.api.routes import settings as settings_router

app = FastAPI(
    title="設備頻譜分析報告比對系統",
    description="比對人工顧問與軟體系統所產出的頻譜分析報告差異",
    version="1.0.0",
)

allowed_origins_env = os.getenv("ALLOWED_ORIGINS", "http://localhost:5173")
allowed_origins = [o.strip() for o in allowed_origins_env.split(",")]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(upload_router.router, prefix="/api", tags=["upload"])
app.include_router(compare_router.router, prefix="/api", tags=["compare"])
app.include_router(settings_router.router, prefix="/api", tags=["settings"])


@app.get("/api/health", tags=["health"])
async def health() -> dict:
    return {"status": "ok"}
