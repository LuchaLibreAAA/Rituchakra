"""Compound livelihood interruption — days the seasonal task cannot be done."""

from __future__ import annotations

from typing import Any


def _clip01(x: float) -> float:
    return max(0.0, min(1.0, x))


def evaluate(f: dict[str, Any], phenology: dict[str, Any], hy: dict[str, Any]) -> dict[str, Any]:
    rain = float(f.get("precip_3d_mm") or 0)
    tmaxs = list(f.get("temp_max") or [30])
    aqi = f.get("naqi")
    aqi_v = int(aqi) if aqi is not None else 0
    rh = float(f.get("rh_now") or 60)
    stage = phenology.get("stage") or "unknown"
    sens = float(phenology.get("stage_score") or 0.5)
    runoff = float(hy.get("runoff_3d_mm") or 0)
    times = list(f.get("daily_times") or [])
    closed: list[str] = []
    reasons: list[str] = []
    n = min(7, max(len(tmaxs), 1))
    for i in range(n):
        tx = float(tmaxs[i]) if i < len(tmaxs) else 30.0
        p = float((f.get("precip_days") or [0] * n)[i] if i < len(f.get("precip_days") or []) else 0)
        date = str(times[i]) if i < len(times) else f"d+{i}"
        heat_lock = tx >= 36 and rh >= 55
        aqi_lock = aqi_v >= 201 and i == 0
        flood_lock = p >= 25 or (i < 3 and runoff >= 14 and p >= 12)
        if heat_lock and aqi_lock:
            closed.append(date)
            reasons.append(f"{date}: heat×AQI field-closed")
        elif flood_lock and stage in {"transplant", "cri", "flowering"}:
            closed.append(date)
            reasons.append(f"{date}: flood blocks {stage}")
        elif heat_lock and tx >= 39:
            closed.append(date)
            reasons.append(f"{date}: extreme heat labour stop")
        elif p >= 45:
            closed.append(date)
            reasons.append(f"{date}: mandi/road rain lock")
    compound = 1.0 if (aqi_v >= 201 and (tmaxs[0] if tmaxs else 30) >= 36) else 0.45 if aqi_v >= 201 or (tmaxs and tmaxs[0] >= 38) else 0.0
    flood_task = _clip01(rain / 55.0) * (0.5 + 0.5 * sens)
    soil_miss = 1.0 if hy.get("flip") == "runoff" and stage in {"transplant", "flowering"} else 0.35 if hy.get("limb") == "wetting" else 0.1
    mandi_block = _clip01((rain - 20) / 40) if rain >= 20 else 0.0
    score = int(round(100 * _clip01(0.34 * compound + 0.30 * flood_task + 0.20 * soil_miss + 0.16 * mandi_block)))
    if compound >= 1.0:
        score = max(score, 52)
    if len(closed) >= 3:
        score = max(score, 72)
    level = "severe" if score >= 70 else "watch" if score >= 40 else "open"
    return {
        "score_pct": score,
        "level": level,
        "task": stage,
        "closed_days": closed,
        "drivers": reasons[:6] or ["seasonal task window is open"],
        "norms": {
            "compound_close": compound,
            "flood_task": flood_task,
            "soil_window": soil_miss,
            "mandi_access": mandi_block,
        },
        "method": "compound livelihood interruption v1",
    }
