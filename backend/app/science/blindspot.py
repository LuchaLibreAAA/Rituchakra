"""Unobserved hydrology: when the quiet dashboard is the wrong story."""

from __future__ import annotations

from typing import Any


def detect(f: dict[str, Any], *, flood_score: int, cap_hit: bool, hy: dict[str, Any]) -> dict[str, Any]:
    rain = float(f.get("precip_3d_mm") or 0)
    soil = float(f.get("soil_m3m3") or 0.25)
    disc = f.get("discharge") or []
    missing_q = not disc
    coast = f.get("coast_km")
    coastal = coast is not None and float(coast) <= 40
    quiet = flood_score < 45 and not cap_hit
    drivers: list[str] = []
    score = 8
    if quiet and rain >= 28 and soil < 0.32:
        score = 48
        drivers.append("Heavy rain but flood card still quiet — drains/embankments unobserved")
    if missing_q:
        score = max(score, 36)
        drivers.append("GloFAS discharge missing at this point")
    if quiet and hy.get("flip") == "runoff":
        score = max(score, 55)
        drivers.append("Hysteresis already on runoff limb while official watch is quiet")
    if coastal and rain >= 18 and quiet:
        score = max(score, 42)
        drivers.append("Near-coast compound (tide/drain) not in GloFAS")
    if rain >= 40 and flood_score < 55:
        score = max(score, 50)
        drivers.append("3-day total large vs flood score — local routing gap")
    if not drivers:
        drivers.append("No strong mismatch between rain/soil and the flood card")
    level = "blind" if score >= 55 else "watch" if score >= 35 else "clear"
    return {
        "score_pct": int(score),
        "level": level,
        "drivers": drivers,
        "method": "unobserved-hydrology residual v1",
        "note": "This is a blind-spot flag, not another flood forecast.",
    }
