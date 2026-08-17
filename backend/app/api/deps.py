from fastapi import Query

from app.schemas.location import Location
from app.services.location_svc import resolve_location


def loc_from_query(
    district: str | None = Query(default=None),
    place: str | None = Query(default=None),
    lat: float | None = Query(default=None),
    lon: float | None = Query(default=None),
) -> Location:
    loc = resolve_location(q=place or district, lat=lat, lon=lon)
    if place and lat is not None and lon is not None:
        loc = loc.model_copy(
            update={
                "lat": lat,
                "lon": lon,
                "place_name": place,
                "place_kind": loc.place_kind if loc.place_kind != "district" else "place",
                "label": f"{place}, {loc.state}" if loc.state else place,
            }
        )
    elif lat is not None and lon is not None:
        loc = loc.model_copy(update={"lat": lat, "lon": lon})
    return loc
