"""Which forecast source to act on today. Sequential trust, not a UI toggle."""

from __future__ import annotations

from typing import Any


def pick(
    *,
    atlas: dict[str, Any],
    cap_hit: bool,
    hy: dict[str, Any],
    regret: dict[str, Any],
) -> dict[str, Any]:
    identified = bool(atlas.get("identified"))
    flip = hy.get("flip") == "runoff"
    if cap_hit:
        source = "imd_cap"
        reason = "Official IMD CAP is active — act on the warning, use NWP only for timing."
        trust_ours = 28
    elif identified and flip:
        source = "ours"
        reason = "Residual atlas is identified here and hysteresis is on the runoff limb."
        trust_ours = 68
    elif identified:
        source = "ours"
        reason = "Regional Open-Meteo residual is identified for this monsoon regime."
        trust_ours = 58
    else:
        source = "trusted"
        reason = "No identified residual — use published Open-Meteo."
        trust_ours = 38
    if regret.get("action") == "hold" and source == "ours":
        reason += " Decision-regret also prefers hold."
    return {
        "source": source,
        "trust_ours_pct": trust_ours,
        "reason": reason,
        "method": "forecast-source policy v1 (not a learned bandit until verify logs exist)",
    }
