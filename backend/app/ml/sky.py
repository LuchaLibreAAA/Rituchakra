"""WMO weather-code → sky caption. Used by Overview live board."""

from __future__ import annotations

from typing import Iterable

COMPASS = [
    (11.25, "N"),
    (33.75, "NNE"),
    (56.25, "NE"),
    (78.75, "ENE"),
    (101.25, "E"),
    (123.75, "ESE"),
    (146.25, "SE"),
    (168.75, "SSE"),
    (191.25, "S"),
    (213.75, "SSW"),
    (236.25, "SW"),
    (258.75, "WSW"),
    (281.25, "W"),
    (303.75, "WNW"),
    (326.25, "NW"),
    (348.75, "NNW"),
    (360.0, "N"),
]

ROSE_ORDER = [
    "N",
    "NNE",
    "NE",
    "ENE",
    "E",
    "ESE",
    "SE",
    "SSE",
    "S",
    "SSW",
    "SW",
    "WSW",
    "W",
    "WNW",
    "NW",
    "NNW",
]

SKY = {
    0: ("Clear sky", "clear"),
    1: ("Mainly clear", "clear"),
    2: ("Partly cloudy", "partly"),
    3: ("Overcast", "cloud"),
    45: ("Fog", "fog"),
    48: ("Depositing rime fog", "fog"),
    51: ("Light drizzle", "rain"),
    53: ("Drizzle", "rain"),
    55: ("Dense drizzle", "rain"),
    61: ("Slight rain", "rain"),
    63: ("Moderate rain", "rain"),
    65: ("Heavy rain", "rain"),
    66: ("Freezing rain", "rain"),
    67: ("Heavy freezing rain", "rain"),
    71: ("Slight snow", "snow"),
    73: ("Snow", "snow"),
    75: ("Heavy snow", "snow"),
    80: ("Rain showers", "rain"),
    81: ("Heavy showers", "rain"),
    82: ("Violent showers", "rain"),
    95: ("Thunderstorm", "storm"),
    96: ("Thunderstorm with hail", "storm"),
    99: ("Severe thunderstorm", "storm"),
}


def sky_label(code: int | None) -> tuple[str, str]:
    if code is None:
        return "Unknown", "cloud"
    if code in SKY:
        return SKY[code]
    if code < 4:
        return SKY[int(code)]
    if 50 <= code < 70:
        return "Rain", "rain"
    if 80 <= code < 90:
        return "Showers", "rain"
    if code >= 95:
        return "Thunderstorm", "storm"
    return f"Code {code}", "cloud"


def compass(deg: float | None) -> str:
    if deg is None:
        return "—"
    d = float(deg) % 360
    for cap, name in COMPASS:
        if d < cap:
            return name
    return "N"


def flow_deg(from_deg: float | None) -> float | None:
    """Meteorological direction is where wind comes from; flow is toward +180°."""
    if from_deg is None:
        return None
    return (float(from_deg) + 180.0) % 360


def flow_compass(from_deg: float | None) -> str:
    return compass(flow_deg(from_deg))


def rose_bins(
    directions: Iterable[float | None],
    speeds: Iterable[float | None] | None = None,
) -> list[dict]:
    acc = {name: {"count": 0, "speed_sum": 0.0} for name in ROSE_ORDER}
    speed_list = list(speeds or [])
    for i, raw in enumerate(directions):
        if raw is None:
            continue
        name = compass(float(raw))
        if name not in acc:
            continue
        acc[name]["count"] += 1
        if i < len(speed_list) and speed_list[i] is not None:
            acc[name]["speed_sum"] += float(speed_list[i])
    out = []
    for name in ROSE_ORDER:
        n = acc[name]["count"]
        out.append(
            {
                "dir": name,
                "count": n,
                "avg_speed": round(acc[name]["speed_sum"] / n, 1) if n else 0.0,
            }
        )
    return out
