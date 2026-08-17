from app.ml.prescribe import _liters, recommend
from app.ml.risk import all_risks


def test_liter_band_matches_example():
    lo, hi, mid = _liters(400.0, 2.5)
    assert mid == 1000
    assert lo == 800
    assert hi == 1200


def test_hold_irrigation_on_heavy_rain():
    f = {
        "precip_3d_mm": 50,
        "precip_prob": [95, 90, 80],
        "soil_m3m3": 0.34,
        "et0_today": 2.0,
        "precip_ratio": 2.5,
        "temp_max": [30, 30, 30],
        "temp_min": [25, 25, 25],
        "rh_now": 90,
        "discharge": [70, 85],
        "discharge_mean": [50, 55],
        "discharge_trend": "rising",
    }
    risks = all_risks(f, cap_hit=True, low_elev=True)
    actions = recommend(f, risks, plot_m2=400)
    hold = next(a for a in actions if a.id == "hold_irrigation")
    assert hold.quant.water_saved_liters_min == 800 or hold.quant.water_saved_liters_min == 960
    assert hold.template_id == "irrigation_hold_rain"
    assert hold.slots["rain_mm"] == 50
