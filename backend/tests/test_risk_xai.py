from app.ml.risk import _round_contributions, all_risks


def test_contributions_sum_to_score():
    f = {
        "precip_ratio": 3.2,
        "precip_3d_mm": 55,
        "precip_today_mm": 30,
        "soil_m3m3": 0.36,
        "discharge": [80.0, 90.0],
        "discharge_mean": [55.0, 60.0],
        "discharge_trend": "rising",
        "et0_today": 2.0,
        "temp_max": [31.0, 30.0, 30.0],
        "temp_min": [25.0, 25.0, 25.0],
        "rh_now": 90,
        "precip_prob": [100, 90, 80],
        "precip_z": 2.1,
    }
    cards = all_risks(f, cap_hit=True, low_elev=True)
    flood = next(c for c in cards if c.id == "flood")
    assert flood.score_pct >= 50
    assert sum(x.contribution_pct for x in flood.factors) == flood.score_pct
    for c in cards:
        assert sum(x.contribution_pct for x in c.factors) == c.score_pct
        assert 0 <= c.score_pct <= 100
        assert 0 <= c.confidence_pct <= 100


def test_round_contributions_exact():
    raw = {"a": 0.31, "b": 0.25, "c": 0.15, "d": 0.07, "e": 0.04}
    out = _round_contributions(raw, 82)
    assert sum(out.values()) == 82
