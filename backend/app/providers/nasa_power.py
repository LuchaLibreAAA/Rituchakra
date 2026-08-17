from __future__ import annotations

from datetime import date, timedelta
from typing import Any

from app import cache
from app.providers.http import client

URL = "https://power.larc.nasa.gov/api/temporal/daily/point"


async def daily_point(lat: float, lon: float, days: int = 16) -> dict[str, Any]:
    key = f"nasa:{round(lat, 2)}:{round(lon, 2)}:{days}"
    hit = cache.get(key)
    if hit is not None:
        return hit
    end = date.today() - timedelta(days=2)
    start = end - timedelta(days=days)
    params = {
        "parameters": "PRECTOTCORR,T2M,RH2M,ALLSKY_SFC_SW_DWN",
        "community": "AG",
        "longitude": lon,
        "latitude": lat,
        "start": start.strftime("%Y%m%d"),
        "end": end.strftime("%Y%m%d"),
        "format": "JSON",
    }
    r = await client().get(URL, params=params)
    r.raise_for_status()
    data = r.json()
    cache.set(key, data, 6 * 60 * 60)
    return data


def precip_series(payload: dict[str, Any]) -> list[float]:
    raw = (
        payload.get("properties", {})
        .get("parameter", {})
        .get("PRECTOTCORR", {})
    )
    vals = []
    for v in raw.values():
        try:
            fv = float(v)
        except (TypeError, ValueError):
            continue
        if fv > -900:
            vals.append(fv)
    return vals
