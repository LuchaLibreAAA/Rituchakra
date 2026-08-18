"""Deterministic 7-day outlook and plot-scale water balance. LLM never computes this."""

from __future__ import annotations

from typing import Any

from app.science.hysteresis import initial_state, step_day


def build_outlook(f: dict[str, Any]) -> dict[str, Any]:
    precip = list(f.get("precip_days") or [])
    probs = list(f.get("precip_prob") or [])
    tmax = list(f.get("temp_max") or [])
    tmin = list(f.get("temp_min") or [])
    et0 = list(f.get("et0_days") or [])
    times = list(f.get("daily_times") or [])
    n = max(len(precip), len(times), 0)
    n = min(7, n)
    st = initial_state(f)
    days: list[dict[str, Any]] = []
    irrigate_on: list[str] = []
    flood_days: list[str] = []
    for i in range(n):
        p = float(precip[i]) if i < len(precip) else 0.0
        e = float(et0[i]) if i < len(et0) else 3.0
        pr = int(probs[i]) if i < len(probs) else 0
        tx = float(tmax[i]) if i < len(tmax) else None
        tn = float(tmin[i]) if i < len(tmin) else None
        date = str(times[i]) if i < len(times) else f"d+{i}"
        st = step_day(st, p, e)
        soil = st["soil"]
        irrigate = p < 4.0 and soil < 0.26 and pr < 55
        flood_watch = p >= 25.0 or st["runoff_mm"] >= 12.0
        if irrigate:
            irrigate_on.append(date)
        if flood_watch:
            flood_days.append(date)
        days.append(
            {
                "date": date,
                "precip_mm": round(p, 1),
                "precip_prob_pct": pr,
                "temp_max_c": round(tx, 1) if tx is not None else None,
                "temp_min_c": round(tn, 1) if tn is not None else None,
                "et0_mm": round(e, 2),
                "soil_m3m3": round(soil, 3),
                "water_balance_mm": round(p - e, 2),
                "runoff_mm": st["runoff_mm"],
                "limb": st["limb"],
                "irrigate": irrigate,
                "flood_watch": flood_watch,
            }
        )
    p7 = sum(float(x) for x in precip[:7])
    e7 = sum(float(x) for x in et0[:7])
    return {
        "days": days,
        "precip_7d_mm": round(p7, 1),
        "et0_7d_mm": round(e7, 2),
        "water_balance_7d_mm": round(p7 - e7, 1),
        "irrigate_dates": irrigate_on,
        "flood_watch_dates": flood_days,
        "method": "open-meteo daily + hysteresis soil v1",
    }


def compact_compare(a: dict[str, Any], b: dict[str, Any]) -> dict[str, Any]:
    """a/b are snapshot.model_dump() fragments."""
    pa, pb = a.get("predictive") or {}, b.get("predictive") or {}
    ra = {r["id"]: r["score_pct"] for r in (a.get("risks") or [])}
    rb = {r["id"]: r["score_pct"] for r in (b.get("risks") or [])}
    ca, cb = (a.get("descriptive") or {}).get("current") or {}, (b.get("descriptive") or {}).get("current") or {}

    def sub(x, y):
        if x is None or y is None:
            return None
        try:
            return round(float(x) - float(y), 2)
        except (TypeError, ValueError):
            return None

    return {
        "rain_3d_mm": sub(pa.get("precip_next_3d_mm"), pb.get("precip_next_3d_mm")),
        "water_balance_7d_mm": sub(pa.get("water_balance_7d_mm"), pb.get("water_balance_7d_mm")),
        "flood_score": sub(ra.get("flood"), rb.get("flood")),
        "drought_score": sub(ra.get("drought"), rb.get("drought")),
        "irrigation_need": sub(ra.get("irrigation_need"), rb.get("irrigation_need")),
        "aqi": sub(ca.get("aqi"), cb.get("aqi")),
        "soil": sub(ca.get("soil_moisture_m3m3"), cb.get("soil_moisture_m3m3")),
    }
