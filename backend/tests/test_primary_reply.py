from app.i18n.templates import render
from app.schemas.dashboard import (
    CurrentConditions,
    DashboardSnapshot,
    Descriptive,
    Diagnostic,
    MapState,
    Predictive,
    Prescriptive,
)
from app.schemas.location import Location
from app.schemas.risk import Prescription, Quant
from app.services.snapshot import primary_reply


def test_primary_reply_hold_bn():
    loc = Location(
        id="x",
        label="Nadia, West Bengal",
        state="West Bengal",
        district="Nadia",
        lat=23.4,
        lon=88.5,
    )
    hold = Prescription(
        id="hold_irrigation",
        priority=1,
        action="hold",
        quant=Quant(water_saved_liters_min=800, water_saved_liters_max=1200),
        template_id="irrigation_hold_rain",
        slots={
            "days": 3,
            "intensity": "heavy",
            "rain_mm": 54.5,
            "prob": 100,
            "liters_min": 960,
            "liters_max": 1440,
        },
    )
    snap = DashboardSnapshot(
        location=loc,
        generated_at="t",
        sources=[],
        descriptive=Descriptive(current=CurrentConditions()),
        diagnostic=Diagnostic(),
        predictive=Predictive(precip_next_3d_mm=54.5, precip_probability_pct=[100]),
        prescriptive=Prescriptive(actions=[hold]),
        risks=[],
        map=MapState(center=[23.4, 88.5]),
    )
    text, tid, slots = primary_reply(snap, "bn", "irrigation")
    assert tid == "irrigation_hold_rain"
    assert "54.5" in text
    assert "960" in text
    assert render("irrigation_hold_rain", "bn", slots) == text


def test_primary_reply_price():
    loc = Location(id="x", label="Nadia", state="West Bengal", district="Nadia", lat=23.4, lon=88.5)
    snap = DashboardSnapshot(
        location=loc,
        generated_at="t",
        sources=[],
        descriptive=Descriptive(current=CurrentConditions()),
        diagnostic=Diagnostic(),
        predictive=Predictive(),
        prescriptive=Prescriptive(),
        risks=[],
        map=MapState(center=[23.4, 88.5]),
        ogd={"mandi": [{"commodity": "Rice", "modal_price": 4900, "market": "Kalyani APMC"}]},
    )
    text, tid, _ = primary_reply(snap, "en", "price")
    assert tid == "mandi_summary"
    assert "Rice" in text
    assert "4900" in text
