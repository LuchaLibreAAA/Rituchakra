"""In-memory TTL cache. Avoids slamming Open-Meteo / CAP on every widget refresh."""

from __future__ import annotations

import time
from threading import Lock
from typing import Any

_lock = Lock()
_store: dict[str, tuple[float, Any]] = {}


def get(key: str) -> Any | None:
    now = time.time()
    with _lock:
        hit = _store.get(key)
        if not hit:
            return None
        expires, value = hit
        if expires < now:
            _store.pop(key, None)
            return None
        return value


def set(key: str, value: Any, ttl_s: float) -> None:
    with _lock:
        _store[key] = (time.time() + ttl_s, value)


def remember(key: str, ttl_s: float, factory):
    hit = get(key)
    if hit is not None:
        return hit
    value = factory()
    set(key, value, ttl_s)
    return value
