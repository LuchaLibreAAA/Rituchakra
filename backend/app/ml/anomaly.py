from __future__ import annotations

from statistics import mean, pstdev
from typing import Any

from app.schemas.dashboard import Anomaly, DiagnosticStory


def compute(
    f: dict[str, Any], nasa_precip: list[float]
) -> tuple[list[Anomaly], list[str], list[DiagnosticStory]]:
    anomalies: list[Anomaly] = []
    drivers: list[str] = []
    stories: list[DiagnosticStory] = []
    z = float(f.get("precip_z") or 0)
    rain3 = float(f.get("precip_3d_mm") or 0)
    soil = float(f.get("soil_m3m3") or 0.25)
    if abs(z) >= 1.2:
        label = "wetter than climatology" if z > 0 else "drier than climatology"
        anomalies.append(Anomaly(variable="precip_vs_nasa_power", z_score=round(z, 2), label=label))
        drivers.append("monsoon pulse" if z > 0 else "rainfall deficit vs climatology")
        stories.append(
            DiagnosticStory(
                id="climatology",
                title="Rain vs NASA POWER climatology",
                why="This point is departing from its recent NASA POWER daily normal.",
                evidence=f"z = {z:.2f}. 3-day rain {rain3:.1f} mm vs climatology ~{float(f.get('clim_3d_mm') or 0):.1f} mm.",
                implication="Wet anomaly raises flood and hold-irrigation odds; dry anomaly raises irrigation need.",
            )
        )
    if soil >= 0.34:
        anomalies.append(Anomaly(variable="soil_moisture", z_score=1.4, label="near-saturated 0–7 cm soil"))
        drivers.append("saturated 0–7 cm soil")
        stories.append(
            DiagnosticStory(
                id="soil",
                title="Topsoil is near saturation",
                why="The 0–7 cm layer has little room left to absorb more rain.",
                evidence=f"Soil moisture {soil:.3f} m³/m³ (field capacity ~0.40).",
                implication="Further rain runs off more readily — drains and low fields matter first.",
            )
        )
    if f.get("discharge_trend") == "rising":
        drivers.append("rising river discharge (GloFAS)")
        d0 = (f.get("discharge") or [None])[0]
        stories.append(
            DiagnosticStory(
                id="discharge",
                title="River discharge is rising",
                why="GloFAS basin routing shows the local river pulse increasing.",
                evidence=f"Trend rising" + (f"; first-step discharge {d0:.1f} m³/s" if d0 is not None else "") + ".",
                implication="Watch embankments and low-lying fields even if rain eases tonight.",
            )
        )
    if rain3 >= 40:
        drivers.append("heavy 3-day rainfall accumulation")
        stories.append(
            DiagnosticStory(
                id="rain3",
                title="Heavy 3-day rain total",
                why="Accumulated rainfall over 72 hours is large enough to waterlog soils and urban drains.",
                evidence=f"{rain3:.1f} mm forecast / observed in the 3-day window.",
                implication="Hold irrigation; keep seed, pumps and livestock off the lowest plots.",
            )
        )
    aqi = f.get("naqi")
    if aqi is not None and int(aqi) >= 201:
        drivers.append(f"CPCB NAQI {int(aqi)} ({f.get('naqi_category') or 'unhealthy'})")
        stories.append(
            DiagnosticStory(
                id="aqi",
                title="Unhealthy official air quality",
                why="CPCB National AQI at the matched station is in the poor-or-worse band.",
                evidence=f"NAQI {int(aqi)} ({f.get('naqi_category')}); dominant {f.get('naqi_dominant') or 'n/a'}.",
                implication="Limit outdoor fieldwork; children and anyone with asthma stay indoors when possible.",
            )
        )
    if nasa_precip:
        clim = mean(nasa_precip)
        anomalies.append(
            Anomaly(
                variable="clim_daily_mm",
                z_score=round((f.get("precip_today_mm", 0) - clim) / (pstdev(nasa_precip) or 1), 2),
                label=f"climatology ~{clim:.1f} mm/day (NASA POWER)",
            )
        )
    if not drivers:
        drivers.append("conditions near seasonal normal")
        stories.append(
            DiagnosticStory(
                id="normal",
                title="Near seasonal normal",
                why="Rain, soil and discharge are not departing sharply from recent climatology.",
                evidence=f"3-day rain {rain3:.1f} mm; soil {soil:.3f} m³/m³.",
                implication="Follow the 7-day outlook; no emergency action is indicated from these drivers.",
            )
        )
    return anomalies, drivers, stories
