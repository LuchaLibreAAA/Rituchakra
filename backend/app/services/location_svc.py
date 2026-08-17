from __future__ import annotations

from app.config import get_settings
from app.data.india_districts import (
    all_districts,
    all_states,
    default_district,
    districts_in_state,
    nearest,
    search_districts,
)
from app.data.india_towns import search_towns
from app.schemas.location import Location


def _from_row(row: dict, **over) -> Location:
    data = {
        "id": row["id"],
        "label": row["label"],
        "country": "IN",
        "state": row["state"],
        "district": row["district"],
        "imd_subdivision": row.get("imd_subdivision"),
        "lat": row["lat"],
        "lon": row["lon"],
        "timezone": "Asia/Kolkata",
        "crop_hint": row.get("crop_hint") or "aman_rice",
        "place_kind": row.get("place_kind") or "district",
        "place_name": row.get("place_name") or row.get("district"),
    }
    data.update({k: v for k, v in over.items() if v is not None})
    return Location(**data)


def _kind_from_feature(code: str | None) -> str:
    c = (code or "").upper()
    if c in {"PPLC", "PPLA", "PPLA2", "PPLA3"}:
        return "city"
    if c in {"PPL", "PPLX", "PPLL"}:
        return "town"
    if c.startswith("ADM"):
        return "district"
    return "place"


def resolve_location(loc: Location | None = None, q: str | None = None,
                     lat: float | None = None, lon: float | None = None) -> Location:
    if loc is not None:
        return loc
    if q:
        towns = search_towns(q, limit=1)
        if towns:
            loc = _town_loc(towns[0])
            if lat is not None and lon is not None:
                return loc.model_copy(update={"lat": lat, "lon": lon})
            return loc
        hits = search_districts(q, limit=1)
        if hits:
            return _from_row(hits[0])
    if lat is not None and lon is not None:
        return _from_row(nearest(lat, lon), lat=lat, lon=lon)
    row = default_district()
    s = get_settings()
    return _from_row(row, lat=s.default_lat, lon=s.default_lon)


def search(q: str, limit: int = 8) -> list[Location]:
    return [_from_row(r) for r in search_districts(q, limit=limit)]


def _town_loc(t: dict) -> Location:
    return Location(
        id=f"town:{t['name'].lower().replace(' ', '_')}_{t['state'][:3].lower()}",
        label=f"{t['name']}, {t['state']}",
        state=t["state"],
        district=t["district"],
        lat=t["lat"],
        lon=t["lon"],
        place_kind=t.get("kind") or "town",
        place_name=t["name"],
    )


async def search_places(q: str, limit: int = 8) -> list[Location]:
    """Districts + curated towns + Open-Meteo India cities."""
    qlow = (q or "").strip().lower()
    towns = [_town_loc(t) for t in search_towns(q, limit=limit)]
    local = search(q, limit=limit)
    extra: list[Location] = []
    try:
        from app.providers import open_meteo

        raw = await open_meteo.geocode_india(q)
    except Exception:
        raw = []
    seen = {(round(x.lat, 2), round(x.lon, 2)) for x in towns + local}
    seen_names = {((x.place_name or x.district).lower(), x.state.lower()) for x in towns}
    for r in raw:
        lat, lon = r.get("latitude"), r.get("longitude")
        if lat is None or lon is None:
            continue
        name = str(r.get("name") or q).strip()
        admin1 = str(r.get("admin1") or "").strip()
        admin2 = str(r.get("admin2") or admin1 or name).strip()
        key = (round(float(lat), 2), round(float(lon), 2))
        if key in seen or (name.lower(), admin1.lower()) in seen_names:
            continue
        seen.add(key)
        extra.append(
            Location(
                id=f"om:{r.get('id') or name.lower().replace(' ', '_')}",
                label=f"{name}, {admin1}" if admin1 else name,
                state=admin1 or "India",
                district=admin2 or name,
                lat=float(lat),
                lon=float(lon),
                place_kind=_kind_from_feature(r.get("feature_code")),
                place_name=name,
            )
        )
    merged = towns + local + extra
    merged.sort(
        key=lambda loc: (
            0 if str(loc.id).startswith("town:") else 1,
            0 if (loc.place_name or "").lower() == qlow else 1,
            0 if loc.place_kind in {"city", "town"} and qlow and qlow in (loc.place_name or "").lower() else 1,
            0 if loc.place_kind == "district" and loc.district.lower() == qlow else 1,
            loc.label,
        )
    )
    # unique by label
    out: list[Location] = []
    used = set()
    for loc in merged:
        if loc.label in used:
            continue
        used.add(loc.label)
        out.append(loc)
        if len(out) >= limit:
            break
    return out


def list_states() -> list[str]:
    return all_states()


def list_districts(state: str | None = None) -> list[Location]:
    rows = districts_in_state(state) if state else all_districts()
    return [_from_row(r) for r in rows]


def nearby(lat: float, lon: float, limit: int = 8) -> list[Location]:
    ranked = sorted(
        all_districts(),
        key=lambda d: (d["lat"] - lat) ** 2 + (d["lon"] - lon) ** 2,
    )
    out: list[Location] = []
    for row in ranked:
        loc = _from_row(row)
        if abs(loc.lat - lat) < 1e-4 and abs(loc.lon - lon) < 1e-4:
            continue
        out.append(loc)
        if len(out) >= limit:
            break
    return out
