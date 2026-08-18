from app.ml.blend import build_dual_predictions
from app.ml.outlook import build_outlook
from app.ml.risk import all_risks
from app.science.hysteresis import fingerprint, initial_state, step_day
from app.science.livelihood import evaluate as live_eval
from app.science.phenology import invert
from app.science.regret import evaluate as regret_eval
from app.science.residual import atlas_lookup, monsoon_regime
from app.science.vernacular import observe_speech
from app.science.wb_xai import attribute


def test_hysteresis_path_dependence():
    wet = initial_state({"soil_m3m3": 0.36, "precip_today_mm": 18, "hourly_precip": [3, 4, 2]})
    dry = initial_state({"soil_m3m3": 0.18, "precip_today_mm": 0, "hourly_precip": [0, 0, 0]})
    a = step_day(wet, 40, 3)
    b = step_day(dry, 40, 3)
    assert a["runoff_mm"] > b["runoff_mm"]
    fp = fingerprint(
        {
            "soil_m3m3": 0.36,
            "precip_today_mm": 20,
            "precip_days": [30, 20, 10],
            "et0_days": [2, 3, 3],
            "daily_times": ["2026-08-17", "2026-08-18", "2026-08-19"],
        }
    )
    assert fp["runoff_3d_mm"] > 0
    assert fp["limb"] in {"wetting", "drying"}


def test_regret_prefers_hold_when_rain_is_coming():
    pack = regret_eval({"precip_3d_mm": 50, "soil_m3m3": 0.34, "et0_today": 2, "precip_prob": [95, 90, 80], "temp_max": [31]})
    assert pack["action"] == "hold"
    assert pack["regret_apply_mm"] > pack["regret_hold_mm"]


def test_livelihood_compound_heat_aqi():
    hy = {"runoff_3d_mm": 2, "flip": "absorbing", "limb": "drying"}
    ph = {"stage": "transplant", "stage_score": 0.88}
    f = {"precip_3d_mm": 4, "temp_max": [40, 39, 38], "naqi": 280, "rh_now": 70, "precip_days": [1, 1, 1], "daily_times": ["d1", "d2", "d3"]}
    out = live_eval(f, ph, hy)
    assert out["score_pct"] >= 40
    assert out["level"] in {"watch", "severe"}


def test_residual_atlas_identified_in_delta():
    f = {"precip_z": 1.2, "precip_3d_mm": 40, "daily_times": ["2026-08-17"]}
    assert monsoon_regime(f) == "active"
    hit = atlas_lookup(23.47, 88.56, "active", 0)
    assert hit["id"] == "gangetic_delta"
    assert hit["identified"] is True
    assert abs(hit["frac"]) >= 0.02


def test_blend_stays_in_honesty_band_with_atlas():
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
        "lat": 23.47,
        "lon": 88.56,
    }
    dual = build_dual_predictions(f)
    t3 = dual["trusted"]["precip_3d_mm"]
    o3 = dual["ours"]["precip_3d_mm"]
    assert abs(o3 - t3) / t3 < 0.2


def test_water_balance_identity_closes():
    hy = {"runoff_3d_mm": 8.0}
    f = {"precip_3d_mm": 40.0, "et0_days": [2.0, 3.0, 3.0], "soil_m3m3": 0.3}
    wb = attribute(f, hy)
    assert abs(wb["checksum_mm"]) < 0.05
    p = wb["parts"]
    assert abs(p["precip_mm"] - p["et0_mm"] - p["runoff_mm"] - p["delta_soil_mm"] - p["deep_plus_unobserved_mm"]) < 0.05


def test_phenology_kharif_august_and_wheat_cri():
    kh = invert({"daily_times": ["2026-08-17"], "et0_today": 3}, crop="aman_rice", mandi=[])
    assert kh["stage"] in {"tillering", "flowering", "transplant"}
    wh = invert({"daily_times": ["2026-12-05"], "et0_today": 2}, crop="wheat", mandi=[])
    assert wh["stage"] == "cri"
    assert wh["stage_score"] >= 0.8


def test_vernacular_tags_bengali_river():
    tags = observe_speech("নদী আসছে, জলাবদ্ধ হয়ে গেছে")
    assert "river_rise" in tags["tags"]
    assert "waterlog" in tags["tags"]


def test_outlook_still_flags_heavy_day():
    out = build_outlook(
        {
            "precip_days": [40.0, 2.0, 0.0, 1.0, 0.0, 0.0, 12.0],
            "precip_prob": [95, 40, 20, 20, 10, 10, 60],
            "temp_max": [30, 31, 32, 33, 34, 33, 31],
            "temp_min": [24, 24, 25, 25, 26, 25, 24],
            "et0_days": [2.0, 3.5, 4.0, 4.2, 4.5, 4.0, 3.0],
            "daily_times": [f"2026-08-{17+i}" for i in range(7)],
            "soil_m3m3": 0.30,
        }
    )
    assert out["days"][0]["flood_watch"] is True
    assert "runoff_mm" in out["days"][0]


def test_livelihood_card_sums_like_other_xai():
    f = {
        "precip_ratio": 3.2,
        "precip_3d_mm": 55,
        "soil_m3m3": 0.36,
        "discharge": [80.0, 90.0],
        "discharge_mean": [55.0, 60.0],
        "discharge_trend": "rising",
        "et0_today": 2.0,
        "temp_max": [31.0, 30.0, 30.0],
        "temp_min": [25.0, 25.0, 25.0],
        "rh_now": 90,
        "hy_runoff_3d_mm": 12,
        "hy_flip": "runoff",
        "hy_memory": 0.7,
        "crop_stage": 0.88,
    }
    cards = all_risks(f, cap_hit=True, low_elev=True)
    live = next(c for c in cards if c.id == "livelihood")
    flood = next(c for c in cards if c.id == "flood")
    assert flood.method == "water_balance_identified_v1"
    assert sum(x.contribution_pct for x in live.factors) == live.score_pct
    assert sum(x.contribution_pct for x in flood.factors) == flood.score_pct
