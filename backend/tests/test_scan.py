from app.agents.intent_router import extract_metric, extract_state
from app.data.india_districts import districts_in_state
from app.services.scan import _drought_score, _flood_score, _sort_key


def test_wb_gazetteer_complete_enough():
    wb = districts_in_state("West Bengal")
    names = {d["district"] for d in wb}
    assert "Nadia" in names
    assert "Cooch Behar" in names
    assert "Purba Medinipur" in names
    assert len(wb) >= 20


def test_extract_state_and_metric():
    q = "Which districts in West Bengal are more likely to get flooded list them."
    assert extract_state(q) == "West Bengal"
    assert extract_metric(q) == "flood"
    assert extract_metric("drought in Rajasthan") == "drought"


def test_flood_score_orders_wet_over_dry():
    wet = {"flood_score": _flood_score(60, 0.38, 22.5, 88.3), "precip_3d_mm": 60}
    dry = {"flood_score": _flood_score(2, 0.18, 26.9, 75.8), "precip_3d_mm": 2}
    assert wet["flood_score"] > dry["flood_score"]
    ranked = sorted([dry, wet], key=_sort_key("flood"))
    assert ranked[0] is wet
    assert _drought_score(1, 0.16) > _drought_score(40, 0.36)
