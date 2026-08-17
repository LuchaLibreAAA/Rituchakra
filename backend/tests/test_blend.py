from app.ml.blend import _nudge_precip, build_dual_predictions


def test_wet_soil_increases_near_term_rain():
    wet, _ = _nudge_precip(20.0, 0, soil=0.36, clim_daily=8.0, precip_z=1.5)
    dry, _ = _nudge_precip(20.0, 0, soil=0.16, clim_daily=8.0, precip_z=-1.5)
    assert wet > 20
    assert dry < 20


def test_dual_predictions_diverge_and_keep_dates():
    f = {
        "precip_days": [30.0, 10.0, 2.0, 1.0, 0.0, 4.0, 8.0],
        "precip_prob": [90, 70, 40, 20, 10, 30, 50],
        "temp_max": [31, 32, 33, 34, 33, 32, 31],
        "temp_min": [24, 24, 25, 25, 25, 24, 24],
        "et0_days": [2, 3, 4, 4, 4, 3, 3],
        "daily_times": [f"2026-08-{17+i}" for i in range(7)],
        "soil_m3m3": 0.36,
        "clim_daily_mm": 8.0,
        "precip_z": 1.8,
        "hourly_precip": [2, 3, 1, 0, 4, 2],
    }
    dual = build_dual_predictions(f)
    assert "trusted" in dual and "ours" in dual
    t3 = dual["trusted"]["precip_3d_mm"]
    o3 = dual["ours"]["precip_3d_mm"]
    assert t3 == 42.0
    assert o3 != t3
    assert abs(o3 - t3) / t3 < 0.2
    assert len(dual["ours"]["days"]) == 7
    assert dual["ours"]["days"][0]["precip_mm"] >= dual["trusted"]["days"][0]["precip_mm"]
