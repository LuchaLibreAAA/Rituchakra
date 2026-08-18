"""Irrigation decision regret. Predictand is the cost of the wrong action."""

from __future__ import annotations

from typing import Any

from app.ml.prescribe import FIELD_CAPACITY, ROOT_MM, _liters


def evaluate(
    f: dict[str, Any],
    *,
    plot_m2: float = 400.0,
    crop_stage: float = 0.55,
    runoff_3d_mm: float = 0.0,
) -> dict[str, Any]:
    rain = float(f.get("precip_3d_mm") or 0)
    soil = float(f.get("soil_m3m3") or 0.25)
    et0 = float(f.get("et0_today") or 3.0)
    probs = f.get("precip_prob") or []
    pmax = max(probs[:3]) if probs else 40
    deficit_mm = max(0.0, (FIELD_CAPACITY - soil) * ROOT_MM)
    # Applying when rain arrives: wasted pump + lodging risk.
    waste_mm = min(rain * 0.45 + runoff_3d_mm * 0.25, 18.0)
    regret_apply = waste_mm * (0.7 + 0.3 * (pmax / 100))
    # Holding when dry: unmet demand, stage-weighted.
    miss_mm = max(0.0, deficit_mm - rain * 0.35) * (0.55 + 0.45 * crop_stage)
    regret_hold = miss_mm * (1.0 - min(pmax, 90) / 140)
    # Heat makes a missed irrigation cost more.
    tmax = (f.get("temp_max") or [30])[0]
    if tmax >= 36:
        regret_hold *= 1.15
    if soil >= 0.33 or rain >= 15 or (pmax >= 70 and rain >= 8):
        action = "hold"
    elif regret_apply + 0.8 < regret_hold:
        action = "hold"
    elif regret_hold + 0.8 < regret_apply and deficit_mm >= 6:
        action = "apply"
    else:
        action = "wait"
    depth = 2.5 if action == "hold" else min(25.0, max(8.0, deficit_mm))
    if action == "hold" and rain >= 40:
        depth = 3.0
    elif action == "hold" and rain < 15:
        depth = 2.0
    lo, hi, mid = _liters(plot_m2, depth)
    return {
        "action": action,
        "regret_hold_mm": round(regret_hold, 2),
        "regret_apply_mm": round(regret_apply, 2),
        "chosen_regret_mm": round(regret_hold if action == "hold" else regret_apply if action == "apply" else min(regret_hold, regret_apply), 2),
        "liters_at_risk_min": lo,
        "liters_at_risk_max": hi,
        "liters_mid": int(round(mid)),
        "deficit_mm": round(deficit_mm, 2),
        "et0_mm": et0,
        "method": "decision-regret v1 (hold vs apply vs wait)",
    }
