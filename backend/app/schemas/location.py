from pydantic import BaseModel, Field


class Location(BaseModel):
    id: str
    label: str
    country: str = "IN"
    state: str
    district: str
    imd_district_id: str | None = None
    imd_station_id: str | None = None
    imd_subdivision: str | None = None
    lat: float
    lon: float
    timezone: str = "Asia/Kolkata"
    crop_hint: str = "aman_rice"
    season_hint: str = "kharif"
    plot_m2: float = Field(default=400.0, description="Assumed smallholder plot")
    place_kind: str = "district"
    place_name: str | None = None
