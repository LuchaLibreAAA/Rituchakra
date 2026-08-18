"""India residual atlas for Open-Meteo. Identified bias, still clipped in blend."""

from __future__ import annotations

from typing import Any

# Box priors from monsoon physiography. Fractions of daily precip, not new rain.
# Sign: + means OM tends to under-wet here in that regime.
_REGIONS: list[dict[str, Any]] = [
    {"id": "sundarbans", "lat": (21.4, 22.6), "lon": (88.2, 89.6), "active": 0.07, "break": -0.03, "pre": 0.02, "post": 0.04, "winter": 0.0},
    {"id": "gangetic_delta", "lat": (22.6, 24.9), "lon": (87.4, 89.3), "active": 0.05, "break": -0.04, "pre": 0.03, "post": 0.02, "winter": 0.0},
    {"id": "wb_hills", "lat": (26.2, 27.6), "lon": (87.8, 89.0), "active": 0.09, "break": 0.02, "pre": 0.04, "post": 0.03, "winter": 0.01},
    {"id": "odisha_coast", "lat": (19.2, 21.8), "lon": (84.6, 87.3), "active": 0.06, "break": -0.02, "pre": 0.05, "post": 0.03, "winter": 0.0},
    {"id": "chotanagpur", "lat": (22.0, 24.8), "lon": (84.0, 87.2), "active": 0.03, "break": -0.03, "pre": 0.04, "post": 0.01, "winter": 0.0},
    {"id": "indo_gangetic", "lat": (24.8, 28.8), "lon": (77.0, 88.2), "active": 0.04, "break": -0.05, "pre": 0.06, "post": 0.01, "winter": 0.0},
    {"id": "northwest", "lat": (26.5, 32.0), "lon": (70.0, 77.5), "active": -0.02, "break": -0.04, "pre": 0.08, "post": -0.02, "winter": 0.01},
    {"id": "deccan", "lat": (14.0, 21.5), "lon": (73.5, 81.0), "active": -0.03, "break": -0.02, "pre": 0.03, "post": 0.0, "winter": 0.0},
    {"id": "west_coast", "lat": (8.2, 20.5), "lon": (72.5, 76.2), "active": 0.08, "break": 0.01, "pre": 0.04, "post": 0.03, "winter": 0.0},
    {"id": "ne_hills", "lat": (23.5, 28.2), "lon": (89.8, 95.5), "active": 0.06, "break": 0.02, "pre": 0.05, "post": 0.04, "winter": 0.01},
]


def _month(f: dict[str, Any]) -> int:
    t = str((f.get("daily_times") or [""])[0] or "")
    try:
        m = int(t[5:7])
        if 1 <= m <= 12:
            return m
    except (TypeError, ValueError):
        pass
    return 8


def monsoon_regime(f: dict[str, Any]) -> str:
    m = _month(f)
    z = float(f.get("precip_z") or 0)
    rain3 = float(f.get("precip_3d_mm") or 0)
    if m in {3, 4, 5}:
        return "pre"
    if m in {10, 11}:
        return "post"
    if m in {12, 1, 2}:
        return "winter"
    if z <= -0.8 or rain3 < 8:
        return "break"
    return "active"


def _region(lat: float, lon: float) -> dict[str, Any] | None:
    for r in _REGIONS:
        la, lb = r["lat"]
        oa, ob = r["lon"]
        if la <= lat <= lb and oa <= lon <= ob:
            return r
    return None


def atlas_lookup(lat: float | None, lon: float | None, regime: str, day_i: int = 0) -> dict[str, Any]:
    if lat is None or lon is None:
        return {"id": "none", "frac": 0.0, "regime": regime, "identified": False}
    reg = _region(float(lat), float(lon))
    if not reg:
        return {"id": "peninsula_default", "frac": 0.0, "regime": regime, "identified": False}
    key = regime if regime in {"active", "break", "pre", "post", "winter"} else "active"
    frac = float(reg.get(key) or 0.0)
    # Skill decays with lead time.
    frac *= max(0.35, 1.0 - 0.09 * day_i)
    return {
        "id": reg["id"],
        "frac": round(frac, 4),
        "regime": regime,
        "identified": abs(frac) >= 0.02,
    }


def describe(f: dict[str, Any], lat: float | None, lon: float | None) -> dict[str, Any]:
    regime = monsoon_regime(f)
    hit = atlas_lookup(lat, lon, regime, 0)
    return {
        **hit,
        "note": "Prior residual of Open-Meteo over India physiography. Applied only inside the ±12% honesty band.",
        "method": "regime-conditioned regional residual atlas v1",
    }
