"""Transparent weighted-linear risk scores. LLM never calls this for narration math."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from app.schemas.risk import Factor, RiskCard

FLOOD_WEIGHTS = {
    "rainfall_anomaly": ("Extreme rainfall anomaly", 0.38),
    "water_level": ("Rising water level / basin QPF", 0.30),
    "soil_sat": ("Saturated soil", 0.18),
    "hist_flood": ("Historical flood pattern", 0.09),
    "drainage": ("Drainage vulnerability", 0.05),
}

DROUGHT_WEIGHTS = {
    "rain_deficit": ("Rainfall deficit vs climatology", 0.40),
    "soil_dry": ("Dry soil profile", 0.28),
    "et0_high": ("High evapotranspiration", 0.18),
    "heat": ("Heat stress", 0.09),
    "hist_drought": ("Seasonal drought pattern", 0.05),
}

HEAT_WEIGHTS = {
    "tmax": ("Maximum temperature", 0.42),
    "rh": ("Humidity / heat index", 0.28),
    "persist": ("Multi-day heat persistence", 0.18),
    "night": ("Warm nights", 0.12),
}

IRRIG_WEIGHTS = {
    "soil_deficit": ("Soil moisture deficit", 0.36),
    "et0": ("Crop evaporative demand", 0.24),
    "no_rain": ("Little rain in forecast", 0.24),
    "stage": ("Crop water-sensitive stage", 0.16),
}

AIR_WEIGHTS = {
    "pm25": ("PM2.5 sub-index", 0.40),
    "pm10": ("PM10 sub-index", 0.25),
    "no2": ("NO2 sub-index", 0.15),
    "ozone": ("Ozone sub-index", 0.12),
    "other": ("Other pollutants (SO2/CO/NH3)", 0.08),
}

SEISMIC_WEIGHTS = {
    "proximity": ("Distance to recent event", 0.42),
    "magnitude": ("Event magnitude", 0.38),
    "depth": ("Shallow focus", 0.20),
}

TSUNAMI_WEIGHTS = {
    "incois": ("INCOIS ITEWS threat", 0.45),
    "usgs_flag": ("USGS tsunami flag", 0.20),
    "source_quake": ("Large Indian-Ocean source", 0.20),
    "coastal": ("Coastal exposure", 0.15),
}


def _clip01(x: float) -> float:
    return max(0.0, min(1.0, x))


def _round_contributions(raw: dict[str, float], score_pct: int) -> dict[str, int]:
    """Integer percents that sum exactly to score_pct."""
    total = sum(raw.values())
    if total <= 0 or score_pct <= 0:
        return {k: 0 for k in raw}
    scaled = {k: score_pct * v / total for k, v in raw.items()}
    floors = {k: int(v) for k, v in scaled.items()}
    rem = score_pct - sum(floors.values())
    order = sorted(scaled, key=lambda k: scaled[k] - floors[k], reverse=True)
    i = 0
    while rem > 0 and order:
        floors[order[i % len(order)]] += 1
        rem -= 1
        i += 1
    return floors


def _severity(score: int) -> str:
    if score >= 75:
        return "high"
    if score >= 50:
        return "medium"
    if score >= 25:
        return "low"
    return "minimal"


def _card(rid: str, label: str, weights: dict, norms: dict[str, float],
          inputs: list[str], missing: list[str], sources: list[str],
          confidence: int, horizon: int = 72) -> RiskCard:
    raw = {k: weights[k][1] * _clip01(norms.get(k, 0.0)) for k in weights}
    mass = sum(raw.values())
    score = int(round(100 * _clip01(mass)))
    contrib = _round_contributions(raw, score)
    factors = [
        Factor(id=k, label=weights[k][0], contribution_pct=contrib[k])
        for k in weights
    ]
    return RiskCard(
        id=rid,
        label=label,
        severity=_severity(score),
        score_pct=score,
        confidence_pct=max(40, min(95, confidence)),
        horizon_hours=horizon,
        factors=factors,
        inputs_used=inputs,
        missing_inputs=missing,
        sources=sources,
        updated_at=datetime.now(timezone.utc).isoformat(),
    )


def flood_risk(f: dict[str, Any], cap_hit: bool, low_elev: bool) -> RiskCard:
    ratio = float(f.get("precip_ratio") or 1.0)
    rain_n = _clip01((ratio - 0.8) / 2.2)
    if f.get("precip_3d_mm", 0) >= 80:
        rain_n = max(rain_n, 0.85)
    elif f.get("precip_3d_mm", 0) >= 40:
        rain_n = max(rain_n, 0.55)

    disc = f.get("discharge") or []
    dmean = f.get("discharge_mean") or []
    if disc and dmean and dmean[0]:
        water_n = _clip01((disc[0] / dmean[0] - 0.8) / 1.4)
    else:
        water_n = 0.35 if f.get("discharge_trend") == "rising" else 0.2
    if f.get("discharge_trend") == "rising":
        water_n = max(water_n, 0.45)

    soil = float(f.get("soil_m3m3") or 0.25)
    soil_n = _clip01((soil - 0.22) / 0.20)

    hist_n = 0.55 if cap_hit else 0.22
    drain_n = 0.6 if low_elev else 0.25
    coast_km = f.get("coast_km")
    if coast_km is not None and float(coast_km) < 35:
        drain_n = max(drain_n, 0.72)

    missing = []
    if not disc:
        missing.append("glofas_discharge")
    conf = 88 - 12 * len(missing)
    if cap_hit:
        conf = min(95, conf + 4)
    return _card(
        "flood", "Flood Risk", FLOOD_WEIGHTS,
        {"rainfall_anomaly": rain_n, "water_level": water_n, "soil_sat": soil_n,
         "hist_flood": hist_n, "drainage": drain_n},
        ["precip_72h", "glofas_discharge", "sm_0_7cm", "imd_cap", "elevation_proxy"],
        missing, ["open-meteo", "imd-cap"], conf,
    )


def drought_risk(f: dict[str, Any]) -> RiskCard:
    ratio = float(f.get("precip_ratio") or 1.0)
    def_n = _clip01((0.7 - ratio) / 0.7)
    soil = float(f.get("soil_m3m3") or 0.25)
    soil_n = _clip01((0.22 - soil) / 0.14)
    et0 = float(f.get("et0_today") or 0)
    et_n = _clip01((et0 - 3.0) / 4.0)
    tmax = (f.get("temp_max") or [30])[0]
    heat_n = _clip01((tmax - 34) / 8)
    return _card(
        "drought", "Drought Risk", DROUGHT_WEIGHTS,
        {"rain_deficit": def_n, "soil_dry": soil_n, "et0_high": et_n,
         "heat": heat_n, "hist_drought": 0.2},
        ["precip_ratio", "sm_0_7cm", "et0", "tmax"],
        [], ["open-meteo", "nasa-power"], 80,
    )


def heat_risk(f: dict[str, Any]) -> RiskCard:
    tmaxs = f.get("temp_max") or [30]
    tmins = f.get("temp_min") or [24]
    tmax = tmaxs[0]
    tmin = tmins[0]
    rh = float(f.get("rh_now") or 60)
    persist = sum(1 for t in tmaxs[:3] if t >= 36) / 3
    return _card(
        "heat", "Heat Risk", HEAT_WEIGHTS,
        {
            "tmax": _clip01((tmax - 32) / 10),
            "rh": _clip01((rh - 40) / 50) * _clip01((tmax - 30) / 10),
            "persist": persist,
            "night": _clip01((tmin - 24) / 8),
        },
        ["tmax", "rh", "tmin"],
        [], ["open-meteo"], 84, horizon=48,
    )


def irrigation_need(f: dict[str, Any]) -> RiskCard:
    soil = float(f.get("soil_m3m3") or 0.25)
    rain = float(f.get("precip_3d_mm") or 0)
    et0 = float(f.get("et0_today") or 3)
    # High score = crop needs water NOW. Incoming rain should suppress this.
    soil_def = _clip01((0.28 - soil) / 0.14)
    et_n = _clip01((et0 - 2.5) / 4)
    no_rain = _clip01((12 - rain) / 12)
    stage = 0.55  # kharif rice default: reproductive-ish monsoon
    return _card(
        "irrigation_need", "Irrigation Need", IRRIG_WEIGHTS,
        {"soil_deficit": soil_def, "et0": et_n, "no_rain": no_rain, "stage": stage * no_rain},
        ["sm_0_7cm", "et0", "precip_72h", "crop_stage"],
        [], ["open-meteo"], 82,
    )


def air_quality_risk(f: dict[str, Any]) -> RiskCard:
    aqi = f.get("naqi")
    pols = f.get("naqi_pollutants") or {}
    if aqi is None and not pols:
        return _card(
            "air_quality", "Air Quality Risk", AIR_WEIGHTS,
            {k: 0.0 for k in AIR_WEIGHTS},
            [], ["cpcb_naqi"], ["data.gov.in"], 45,
        )
    if aqi is None:
        aqi = max(pols.values())
    pm25 = float(pols.get("PM2.5") or pols.get("PM25") or 0)
    pm10 = float(pols.get("PM10") or 0)
    no2 = float(pols.get("NO2") or 0)
    o3 = float(pols.get("OZONE") or pols.get("O3") or 0)
    other = max(
        [float(v) for k, v in pols.items() if k not in {"PM2.5", "PM25", "PM10", "NO2", "OZONE", "O3"}] or [0]
    )
    return _card(
        "air_quality", "Air Quality Risk", AIR_WEIGHTS,
        {
            "pm25": _clip01(pm25 / 400),
            "pm10": _clip01(pm10 / 400),
            "no2": _clip01(no2 / 400),
            "ozone": _clip01(o3 / 400),
            "other": _clip01(other / 400),
        },
        ["cpcb_naqi", *list(pols.keys())[:6]],
        [],
        ["data.gov.in / CPCB"],
        86,
        horizon=24,
    )


def seismic_risk(quakes: list[dict] | None = None) -> RiskCard:
    quakes = quakes or []
    q0 = quakes[0] if quakes else {}
    dist = float(q0.get("distance_km") or 2500)
    mag = float(q0.get("mag") or 0)
    depth = float(q0.get("depth_km") or 90)
    missing = [] if quakes else ["usgs_events"]
    return _card(
        "seismic",
        "Seismic Risk",
        SEISMIC_WEIGHTS,
        {
            "proximity": _clip01((450 - dist) / 450),
            "magnitude": _clip01((mag - 3.2) / 3.8),
            "depth": _clip01((80 - depth) / 80),
        },
        ["usgs_fdsn"] if quakes else [],
        missing,
        ["usgs-fdsn"],
        70 if quakes else 42,
        horizon=24,
    )


def tsunami_risk(
    tsunami: list[dict] | None = None,
    quakes: list[dict] | None = None,
    coast_km: float | None = None,
) -> RiskCard:
    tsunami = tsunami or []
    quakes = quakes or []
    threat = 1.0 if any(t.get("threat") for t in tsunami) else 0.12 if tsunami else 0.0
    flag = 1.0 if any(q.get("tsunami_flag") and float(q.get("mag") or 0) >= 6 for q in quakes) else 0.0
    src = 0.7 if any(float(q.get("mag") or 0) >= 6.5 for q in quakes) else 0.1
    coast = _clip01((150 - float(coast_km)) / 150) if coast_km is not None else 0.15
    missing = []
    if not tsunami:
        missing.append("incois_itews")
    return _card(
        "tsunami",
        "Tsunami Risk",
        TSUNAMI_WEIGHTS,
        {"incois": threat, "usgs_flag": flag, "source_quake": src, "coastal": coast},
        ["incois_itews", "usgs_fdsn", "coast_distance"],
        missing,
        ["incois-itews", "usgs-fdsn"],
        78 if tsunami else 50,
        horizon=12,
    )


def all_risks(
    f: dict[str, Any],
    *,
    cap_hit: bool,
    low_elev: bool,
    quakes: list[dict] | None = None,
    tsunami: list[dict] | None = None,
) -> list[RiskCard]:
    return [
        flood_risk(f, cap_hit, low_elev),
        drought_risk(f),
        heat_risk(f),
        irrigation_need(f),
        air_quality_risk(f),
        seismic_risk(quakes),
        tsunami_risk(tsunami, quakes, f.get("coast_km")),
    ]
