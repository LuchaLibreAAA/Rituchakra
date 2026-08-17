"""Sparse India–Andaman coastline points for nearest-coast marine fallback.

Open-Meteo marine has no grid over many deltas (Haldia, Sundarbans, etc.).
We snap to the nearest named coast and say so — never “no marine grid”.
"""

from __future__ import annotations

from math import atan2, cos, radians, sin, sqrt

# name, lat, lon
COAST: list[tuple[str, float, float]] = [
    ("Jakhau", 23.24, 68.72),
    ("Dwarka", 22.24, 68.97),
    ("Okha", 22.47, 69.08),
    ("Mandvi", 22.83, 69.36),
    ("Porbandar", 21.64, 69.61),
    ("Veraval", 20.91, 70.37),
    ("Kandla", 23.03, 70.22),
    ("Bhavnagar", 21.76, 72.15),
    ("Surat / Hazira", 21.10, 72.65),
    ("Mumbai", 18.95, 72.84),
    ("Alibag", 18.64, 72.88),
    ("Ratnagiri", 16.99, 73.29),
    ("Mormugao", 15.41, 73.79),
    ("Karwar", 14.80, 74.13),
    ("Mangaluru", 12.87, 74.84),
    ("Kozhikode", 11.25, 75.78),
    ("Kochi", 9.97, 76.24),
    ("Kollam", 8.88, 76.60),
    ("Thiruvananthapuram", 8.48, 76.95),
    ("Kanyakumari", 8.08, 77.54),
    ("Thoothukudi", 8.76, 78.13),
    ("Rameswaram", 9.28, 79.31),
    ("Nagapattinam", 10.76, 79.84),
    ("Puducherry", 11.93, 79.83),
    ("Cuddalore", 11.75, 79.75),
    ("Chennai", 13.08, 80.29),
    ("Ennore", 13.23, 80.33),
    ("Nellore coast", 14.45, 80.12),
    ("Machilipatnam", 16.17, 81.13),
    ("Kakinada", 16.99, 82.25),
    ("Visakhapatnam", 17.69, 83.22),
    ("Kalingapatnam", 18.34, 84.12),
    ("Gopalpur", 19.26, 84.91),
    ("Puri", 19.80, 85.83),
    ("Paradip", 20.26, 86.67),
    ("Chandipur", 21.45, 87.02),
    ("Digha", 21.63, 87.52),
    ("Contai", 21.78, 87.75),
    ("Haldia", 22.07, 88.07),
    ("Sagar Island", 21.65, 88.05),
    ("Kakdwip", 21.88, 88.18),
    ("Fraserganj", 21.57, 88.26),
    ("Sundarbans coast", 21.95, 88.85),
    ("Port Blair", 11.67, 92.74),
    ("Car Nicobar", 9.17, 92.78),
]


def _km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    r = 6371.0
    p1, p2 = radians(lat1), radians(lat2)
    dp, dl = radians(lat2 - lat1), radians(lon2 - lon1)
    a = sin(dp / 2) ** 2 + cos(p1) * cos(p2) * sin(dl / 2) ** 2
    return 2 * r * atan2(sqrt(a), sqrt(max(0.0, 1 - a)))


def nearest_coast(lat: float, lon: float) -> dict:
    best = min(COAST, key=lambda c: _km(lat, lon, c[1], c[2]))
    km = round(_km(lat, lon, best[1], best[2]), 1)
    return {"name": best[0], "lat": best[1], "lon": best[2], "km": km}
