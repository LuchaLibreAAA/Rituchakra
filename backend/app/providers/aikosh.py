"""AIKosh client. Dataset list / metadata require AIKOSH_API_KEY."""

from __future__ import annotations

from typing import Any

from app.config import get_settings
from app.providers.http import client


async def search_datasets(q: str) -> tuple[list[dict[str, Any]], str]:
    settings = get_settings()
    if not settings.aikosh_api_key:
        return [], "missing_key"
    headers = {"Authorization": f"Bearer {settings.aikosh_api_key}"}
    try:
        r = await client().get(
            f"{settings.aikosh_api_base.rstrip('/')}/datasets",
            params={"q": q},
            headers=headers,
        )
        if r.status_code == 401:
            return [], "unauthorized"
        r.raise_for_status()
        data = r.json()
        if isinstance(data, list):
            return data, "ok"
        return data.get("results") or data.get("data") or [], "ok"
    except Exception:
        return [], "error"
