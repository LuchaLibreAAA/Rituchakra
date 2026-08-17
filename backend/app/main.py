from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import chat, dashboard, geo
from app.config import get_settings
from app.llm import ollama_client
from app.providers.http import aclose
from app.services.location_svc import resolve_location


@asynccontextmanager
async def lifespan(_: FastAPI):
    yield
    await aclose()


settings = get_settings()
app = FastAPI(
    title="RainFall Environmental Intelligence",
    version="0.2.0",
    description="India-first environmental dashboard. ML/APIs compute; the LLM orchestrates tools and narrates.",
    lifespan=lifespan,
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(dashboard.router, prefix="/api")
app.include_router(geo.router, prefix="/api")
app.include_router(chat.router, prefix="/api")


@app.get("/api/health")
async def health():
    ollama_ok, ollama_msg = await ollama_client.ping()
    loc = resolve_location()
    return {
        "ok": True,
        "default_location": loc.model_dump(),
        "ollama": {"ok": ollama_ok, "detail": ollama_msg, "model": settings.ollama_model},
        "keys": {
            "imd_api_key": bool(settings.imd_api_key),
            "aikosh_api_key": bool(settings.aikosh_api_key),
            "data_gov_in_api_key": bool(settings.data_gov_in_api_key),
        },
        "notes": {
            "imd_rest": "api.imd.gov.in requires IP whitelist — CAP alerts are used until then.",
            "inject_keys": "See backend/.env.example",
        },
    }
