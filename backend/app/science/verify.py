"""Skill proxy until IMD station verify is wired. Does not invent outcomes."""

from __future__ import annotations

from typing import Any


def skill_proxy(f: dict[str, Any], atlas: dict[str, Any]) -> dict[str, Any]:
    today = float(f.get("precip_today_mm") or 0)
    clim = float(f.get("clim_daily_mm") or 0)
    z = float(f.get("precip_z") or 0)
    err = abs(today - clim)
    return {
        "today_mm": round(today, 2),
        "climatology_mm": round(clim, 2),
        "abs_vs_clim_mm": round(err, 2),
        "precip_z": round(z, 2),
        "atlas_id": atlas.get("id"),
        "atlas_frac": atlas.get("frac"),
        "method": "NASA POWER climatology proxy — not IMD station verification",
        "note": "True skill needs IMD/CWC outcomes. This only documents the residual vs climatology.",
    }
