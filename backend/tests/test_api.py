from fastapi.testclient import TestClient

from app.main import app
from app.services.location_svc import search

client = TestClient(app)


def test_health():
    r = client.get("/api/health")
    assert r.status_code == 200
    body = r.json()
    assert body["ok"] is True
    assert body["default_location"]["district"] == "Nadia"


def test_geo_search_and_nearby():
    r = client.get("/api/geo/search", params={"q": "Pune"})
    assert r.status_code == 200
    assert r.json()["results"][0]["district"] == "Pune"
    loc = search("Kolkata")[0]
    n = client.get("/api/geo/nearby", params={"lat": loc.lat, "lon": loc.lon, "limit": 3})
    assert n.status_code == 200
    assert len(n.json()["results"]) == 3


def test_states_and_districts():
    s = client.get("/api/states")
    assert s.status_code == 200
    assert "West Bengal" in s.json()["states"]
    d = client.get("/api/districts", params={"state": "West Bengal"})
    assert d.status_code == 200
    assert d.json()["count"] >= 20


def test_map_layers():
    r = client.get("/api/map/layers")
    assert r.status_code == 200
    ids = {b["id"] for b in r.json()["basemaps"]}
    assert {"positron", "streets", "satellite", "terrain"} <= ids
    overlays = {o["id"]: o for o in r.json()["overlays"]}
    assert overlays["bhuvan_geomorph"]["url"] == "/api/map/wms"
    assert "WB_LGEOM" in overlays["bhuvan_geomorph"]["layers"]
