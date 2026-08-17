"""Multi-factor flood / tsunami / seismic outlook. Numbers stay off the LLM."""

from __future__ import annotations

from typing import Any


def _clip(x: float, lo: float = 0.0, hi: float = 100.0) -> float:
    return max(lo, min(hi, x))


def build_hazard_forecast(
    f: dict[str, Any],
    *,
    flood_score: int,
    quakes: list[dict] | None = None,
    tsunami: list[dict] | None = None,
    coast_km: float | None = None,
    cap_hit: bool = False,
) -> dict[str, Any]:
    quakes = quakes or []
    tsunami = tsunami or []
    rain = float(f.get("precip_3d_mm") or 0)
    soil = float(f.get("soil_m3m3") or 0.25)
    disc = f.get("discharge") or []
    trend = str(f.get("discharge_trend") or "steady")
    flood_days = []
    precip = list(f.get("precip_days") or [])
    times = list(f.get("daily_times") or [])
    for i, p in enumerate(precip[:7]):
        date = str(times[i]) if i < len(times) else f"d+{i}"
        rising = trend == "rising" and i <= 2
        if float(p) >= 25 or (rising and float(p) >= 12) or (soil >= 0.34 and float(p) >= 18):
            flood_days.append(date)

    flood = {
        "score_pct": int(flood_score),
        "level": "high" if flood_score >= 70 else "watch" if flood_score >= 45 else "quiet",
        "days": flood_days,
        "drivers": [
            f"3-day rain {rain:.0f} mm",
            f"0–7 cm soil {soil:.2f}",
            f"GloFAS {trend}" + (f" ({disc[0]:.0f} m³/s)" if disc else ""),
            "IMD CAP active" if cap_hit else "no local IMD CAP",
            f"coast {coast_km:.0f} km" if coast_km is not None else "coast distance n/a",
        ],
        "method": "rain + soil + GloFAS discharge + elevation proxy + IMD CAP",
        "source": "Open-Meteo GloFAS + local-ml + IMD CAP",
    }

    threat = any(t.get("threat") for t in tsunami)
    flagged = any(q.get("tsunami_flag") and float(q.get("mag") or 0) >= 6 for q in quakes)
    ocean_big = any(float(q.get("mag") or 0) >= 6.5 for q in quakes)
    coastal = coast_km is not None and coast_km <= 80
    tsu_score = 8
    if threat:
        tsu_score = 82
    elif flagged and coastal:
        tsu_score = 58
    elif flagged:
        tsu_score = 40
    elif ocean_big and coastal:
        tsu_score = 28
    elif tsunami:
        tsu_score = 12
    latest = tsunami[0] if tsunami else None
    tsunami_out = {
        "score_pct": int(_clip(tsu_score)),
        "level": "warning" if threat else "watch" if tsu_score >= 25 else "quiet",
        "threat": bool(threat),
        "latest_title": (latest or {}).get("title"),
        "latest_body": (latest or {}).get("body"),
        "coast_km": coast_km,
        "method": "INCOIS ITEWS evaluation + USGS tsunami flag + coast distance + source magnitude",
        "source": "INCOIS ITEWS + USGS FDSN",
    }

    q0 = quakes[0] if quakes else {}
    mag = float(q0.get("mag") or 0)
    dist = float(q0.get("distance_km") or 9e9)
    depth = float(q0.get("depth_km") or 80)
    prox = _clip((450 - dist) / 450 * 100)
    mag_n = _clip((mag - 3.2) / 3.8 * 100)
    shallow = _clip((80 - depth) / 80 * 100)
    seis = int(round(0.42 * prox + 0.38 * mag_n + 0.20 * shallow))
    seismic_out = {
        "score_pct": seis,
        "level": "high" if seis >= 70 else "watch" if seis >= 40 else "quiet",
        "nearest_mag": mag or None,
        "nearest_km": None if dist > 8000 else round(dist, 0),
        "nearest_place": q0.get("place"),
        "depth_km": q0.get("depth_km"),
        "method": "USGS 7-day India–Indian Ocean catalog: magnitude × proximity × depth",
        "source": "USGS FDSN (NCS has no public JSON)",
    }

    return {
        "flood": flood,
        "tsunami": tsunami_out,
        "seismic": seismic_out,
        "method": "multi-dimensional local model; trusted weather/flood numbers stay on Open-Meteo",
    }
