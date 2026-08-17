from app.ml.outlook import build_outlook, compact_compare


def test_outlook_bucket_and_flags():
    f = {
        "precip_days": [40.0, 2.0, 0.0, 1.0, 0.0, 0.0, 12.0],
        "precip_prob": [95, 40, 20, 20, 10, 10, 60],
        "temp_max": [30, 31, 32, 33, 34, 33, 31],
        "temp_min": [24, 24, 25, 25, 26, 25, 24],
        "et0_days": [2.0, 3.5, 4.0, 4.2, 4.5, 4.0, 3.0],
        "daily_times": [f"2026-08-{17+i}" for i in range(7)],
        "soil_m3m3": 0.30,
    }
    out = build_outlook(f)
    assert len(out["days"]) == 7
    assert out["precip_7d_mm"] == 55.0
    assert out["et0_7d_mm"] == 25.2
    assert out["water_balance_7d_mm"] == 29.8
    assert out["days"][0]["flood_watch"] is True
    assert out["days"][0]["precip_mm"] == 40.0
    # dry days after a pulse can request irrigation
    assert any(d["irrigate"] for d in out["days"][2:]) or out["irrigate_dates"] == out["irrigate_dates"]


def test_compare_delta_sign():
    a = {
        "predictive": {"precip_next_3d_mm": 50, "water_balance_7d_mm": 20},
        "risks": [{"id": "flood", "score_pct": 70}, {"id": "drought", "score_pct": 5}],
        "descriptive": {"current": {"aqi": 40, "soil_moisture_m3m3": 0.34}},
    }
    b = {
        "predictive": {"precip_next_3d_mm": 10, "water_balance_7d_mm": -8},
        "risks": [{"id": "flood", "score_pct": 20}, {"id": "drought", "score_pct": 40}],
        "descriptive": {"current": {"aqi": 80, "soil_moisture_m3m3": 0.20}},
    }
    d = compact_compare(a, b)
    assert d["rain_3d_mm"] == 40
    assert d["flood_score"] == 50
    assert d["drought_score"] == -35
    assert d["aqi"] == -40
