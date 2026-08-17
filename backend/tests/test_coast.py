from app.data.india_coast import nearest_coast
from app.ml.hazards_outlook import build_hazard_forecast


def test_nadia_snaps_to_bengal_coast():
    c = nearest_coast(23.47, 88.55)
    assert c["km"] < 200
    assert c["name"] in {"Haldia", "Digha", "Kakdwip", "Sundarbans coast", "Contai", "Sagar Island"}


def test_hazard_forecast_quiet_inland():
    out = build_hazard_forecast(
        {"precip_3d_mm": 8, "soil_m3m3": 0.24, "discharge_trend": "steady", "precip_days": [2, 1, 0]},
        flood_score=22,
        quakes=[{"mag": 4.1, "distance_km": 1400, "depth_km": 80, "place": "far"}],
        tsunami=[{"title": "ITEWS M6.8 — no tsunami threat for India", "threat": False}],
        coast_km=180,
        cap_hit=False,
    )
    assert out["tsunami"]["level"] == "quiet"
    assert out["flood"]["score_pct"] == 22
    assert out["seismic"]["nearest_km"] == 1400
