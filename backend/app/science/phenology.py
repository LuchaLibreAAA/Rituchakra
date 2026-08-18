"""Crop stage from calendar + Agmarknet inversion. Not NDVI."""

from __future__ import annotations

from typing import Any


def _month(f: dict[str, Any]) -> int:
    t = str((f.get("daily_times") or [""])[0] or "")
    try:
        m = int(t[5:7])
        if 1 <= m <= 12:
            return m
    except (TypeError, ValueError):
        pass
    return 8


def _crop_family(crop: str) -> str:
    c = (crop or "").lower()
    if any(k in c for k in ("wheat", "mustard", "gram", "potato", "rabi")):
        return "rabi"
    if any(k in c for k in ("veg", "moong", "zaid")):
        return "zaid"
    return "kharif"


def _calendar_stage(family: str, month: int) -> tuple[str, float]:
    """Return (name, water-sensitivity 0–1)."""
    if family == "rabi":
        if month in {11, 12}:
            return "cri", 0.92
        if month in {1, 2}:
            return "grain_fill", 0.80
        if month == 3:
            return "maturity", 0.35
        return "off_season", 0.20
    if family == "zaid":
        return ("peak_et", 0.78) if month in {3, 4, 5} else ("off_season", 0.25)
    # kharif rice / maize
    if month in {6, 7}:
        return "transplant", 0.88
    if month == 8:
        return "tillering", 0.70
    if month == 9:
        return "flowering", 0.90
    if month == 10:
        return "grain_fill", 0.75
    return "off_season", 0.30


def invert(
    f: dict[str, Any],
    *,
    crop: str = "aman_rice",
    mandi: list[dict] | None = None,
) -> dict[str, Any]:
    family = _crop_family(crop)
    month = _month(f)
    stage, sens = _calendar_stage(family, month)
    et0 = float(f.get("et0_today") or 3.0)
    rain = float(f.get("precip_3d_mm") or 0)
    rows = mandi or []
    prices = [float(r.get("modal_price") or 0) for r in rows if r.get("modal_price")]
    n_arrivals = len([r for r in rows if r.get("commodity")])
    # Few arrivals + high ET + dry rain → market-visible stress.
    stress = 0.0
    if n_arrivals <= 1 and et0 >= 4.5 and rain < 8:
        stress = 0.55
    elif n_arrivals == 0 and rain < 5:
        stress = 0.35
    if prices and max(prices) > 0 and n_arrivals <= 2 and et0 >= 4:
        stress = max(stress, 0.40)
    stage_score = min(1.0, sens * (1.0 + 0.25 * stress))
    return {
        "family": family,
        "stage": stage,
        "stage_score": round(stage_score, 3),
        "mandi_stress": round(stress, 3),
        "arrivals": n_arrivals,
        "month": month,
        "method": "crop calendar + Agmarknet arrival inversion v1",
    }
