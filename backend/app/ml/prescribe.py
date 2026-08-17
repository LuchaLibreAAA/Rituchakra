"""Deterministic interventions. Liter estimates are computed here — never by the LLM."""

from __future__ import annotations

from typing import Any

from app.schemas.risk import Prescription, Quant, RiskCard

FIELD_CAPACITY = 0.40
WILTING = 0.15
ROOT_MM = 70.0  # 0–7 cm layer water equivalent


def _liters(plot_m2: float, depth_mm: float) -> tuple[int, int, float]:
    mid = plot_m2 * depth_mm
    return int(round(mid * 0.8)), int(round(mid * 1.2)), mid


def recommend(f: dict[str, Any], risks: list[RiskCard], plot_m2: float = 400.0,
              crop: str = "aman_rice") -> list[Prescription]:
    rain = float(f.get("precip_3d_mm") or 0)
    probs = f.get("precip_prob") or []
    soil = float(f.get("soil_m3m3") or 0.25)
    flood = next((r for r in risks if r.id == "flood"), None)
    drought = next((r for r in risks if r.id == "drought"), None)
    heat = next((r for r in risks if r.id == "heat"), None)
    irrig = next((r for r in risks if r.id == "irrigation_need"), None)

    out: list[Prescription] = []
    deficit_mm = max(0.0, (FIELD_CAPACITY - soil) * ROOT_MM)

    # Incoming rain → hold irrigation (farmer story)
    if rain >= 15 or (probs and max(probs[:3]) >= 70 and rain >= 8) or soil >= 0.32:
        depth = 2.5
        if rain >= 40:
            depth = 3.0
        elif rain < 15:
            depth = 2.0
        lo, hi, _ = _liters(plot_m2, depth)
        intensity = "heavy" if rain >= 50 else "moderate to heavy" if rain >= 20 else "light to moderate"
        out.append(
            Prescription(
                id="hold_irrigation",
                priority=1,
                action=f"Do not irrigate in the next 24 hours — {intensity} rain is likely.",
                rationale_codes=["rain_72h_ge_threshold", "soil_near_field_capacity"] if soil >= 0.30 else ["rain_72h_ge_threshold"],
                quant=Quant(
                    water_saved_liters_min=lo,
                    water_saved_liters_max=hi,
                    method="area_m2 * depth_mm_avoided",
                    assumptions={"plot_m2": plot_m2, "depth_mm_avoided": depth, "crop": crop},
                ),
                confidence_pct=min(92, 70 + int(min(rain, 40))),
                template_id="irrigation_hold_rain",
                slots={
                    "days": 3,
                    "intensity": intensity,
                    "rain_mm": round(rain, 1),
                    "prob": max(probs[:3]) if probs else 60,
                    "liters_min": lo,
                    "liters_max": hi,
                },
                why=f"{intensity.capitalize()} rain ({rain:.0f} mm / 3d) will refill the 0–7 cm layer.",
                when="Next 24 hours",
                who="farmer / plot manager",
            )
        )
    elif irrig and irrig.score_pct >= 45:
        # Apply a light irrigation matching remaining deficit, capped
        depth = min(25.0, max(8.0, deficit_mm))
        lo, hi, _ = _liters(plot_m2, depth)
        out.append(
            Prescription(
                id="apply_irrigation",
                priority=1,
                action=f"Apply a light irrigation of about {depth:.0f} mm today; little rain is expected.",
                rationale_codes=["soil_deficit", "low_forecast_rain"],
                quant=Quant(
                    water_saved_liters_min=None,
                    water_saved_liters_max=None,
                    method="deficit_fill",
                    assumptions={"plot_m2": plot_m2, "depth_mm": depth, "crop": crop},
                ),
                confidence_pct=78,
                template_id="irrigation_apply",
                slots={"depth_mm": round(depth, 0), "rain_mm": round(rain, 1), "liters": int(plot_m2 * depth)},
                why="Soil is below a comfortable threshold and the 3-day rain total is small.",
                when="This morning or evening, not midday",
                who="farmer / plot manager",
            )
        )

    if flood and flood.score_pct >= 55:
        out.append(
            Prescription(
                id="flood_prep",
                priority=0,
                action="Move livestock, seed, and pumps to higher ground; clear local drains; avoid low-lying fields.",
                rationale_codes=["flood_risk_elevated"],
                confidence_pct=flood.confidence_pct,
                template_id="flood_prep",
                slots={"score": flood.score_pct},
                why=f"Flood score is {flood.score_pct}% from rain, soil saturation and rising discharge.",
                when="Before the next heavy pulse",
                who="household + livestock keeper",
            )
        )

    if drought and drought.score_pct >= 55:
        out.append(
            Prescription(
                id="drought_conserve",
                priority=2,
                action="Mulch, irrigate at dawn/dusk only, and skip non-critical plots to stretch stored water.",
                rationale_codes=["drought_risk_elevated"],
                confidence_pct=drought.confidence_pct,
                template_id="drought_conserve",
                slots={"score": drought.score_pct},
                why=f"Drought score {drought.score_pct}% — rain is below climatology and the soil is dry.",
                when="Until the next wetting rain",
                who="farmer / water manager",
            )
        )

    if heat and heat.score_pct >= 55:
        out.append(
            Prescription(
                id="heat_protect",
                priority=2,
                action="Avoid midday field work; keep drinking water in the field; provide shade for livestock.",
                rationale_codes=["heat_risk_elevated"],
                confidence_pct=heat.confidence_pct,
                template_id="heat_protect",
                slots={"score": heat.score_pct},
                why=f"Heat score {heat.score_pct}% from high afternoon temperature and humidity.",
                when="10:00–16:00 local",
                who="field workers + livestock keeper",
            )
        )

    aqi = f.get("naqi")
    air = next((r for r in risks if r.id == "air_quality"), None)
    if aqi is not None and aqi >= 201:
        out.append(
            Prescription(
                id="aqi_protect",
                priority=2,
                action=f"National AQI is {int(aqi)} — limit outdoor fieldwork and keep N95/cloth cover for dust.",
                rationale_codes=["cpcb_naqi_poor"],
                confidence_pct=air.confidence_pct if air else 80,
                template_id="aqi_protect",
                slots={
                    "aqi": int(aqi),
                    "category": f.get("naqi_category") or "",
                    "pollutant": f.get("naqi_dominant") or "",
                },
                why=f"Official CPCB NAQI is {int(aqi)} ({f.get('naqi_category') or 'unhealthy'}).",
                when="Until NAQI falls below 200",
                who="everyone outdoors, especially children and anyone with asthma",
            )
        )

    seis = next((r for r in risks if r.id == "seismic"), None)
    if seis and seis.score_pct >= 55:
        out.append(
            Prescription(
                id="seismic_prep",
                priority=1,
                action="Stay clear of unreinforced walls and overhead storage; keep a torch and shoes by the bed.",
                rationale_codes=["seismic_watch"],
                confidence_pct=seis.confidence_pct,
                why=f"Nearest catalogued event scores seismic risk {seis.score_pct}% (USGS India box).",
                when="While a nearby event is in the 7-day catalog",
                who="household",
            )
        )
    tsu = next((r for r in risks if r.id == "tsunami"), None)
    if tsu and tsu.score_pct >= 40:
        out.append(
            Prescription(
                id="tsunami_prep",
                priority=0,
                action="If you are on the open coast, move inland or to higher ground and follow INCOIS / district disaster instructions.",
                rationale_codes=["tsunami_watch"],
                confidence_pct=tsu.confidence_pct,
                why="INCOIS ITEWS and/or a USGS tsunami-flagged source earthquake is active.",
                when="Immediately if INCOIS issues a threat; otherwise stay alert",
                who="coastal households and harbour staff",
            )
        )

    out.sort(key=lambda p: p.priority)
    return out
