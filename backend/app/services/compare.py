from __future__ import annotations

from typing import Any

from app.ml.outlook import compact_compare
from app.schemas.location import Location
from app.services.location_svc import resolve_location
from app.services.snapshot import build_snapshot


def _card(snap) -> dict[str, Any]:
    return {
        "location": snap.location.model_dump(),
        "predictive": snap.predictive.model_dump(),
        "descriptive": {"current": snap.descriptive.current.model_dump()},
        "risks": [r.model_dump() for r in snap.risks],
        "warnings": [w.model_dump() for w in snap.prescriptive.warnings[:3]],
        "actions": [a.model_dump() for a in snap.prescriptive.actions[:3]],
    }


async def compare(query_a: str, query_b: str, loc_a: Location | None = None,
                  loc_b: Location | None = None) -> dict[str, Any]:
    a = loc_a or resolve_location(q=query_a)
    b = loc_b or resolve_location(q=query_b)
    sa = await build_snapshot(a)
    sb = await build_snapshot(b)
    ca, cb = _card(sa), _card(sb)
    return {
        "a": ca,
        "b": cb,
        "delta_a_minus_b": compact_compare(ca, cb),
        "note": "Positive rain/flood delta means A is wetter / riskier than B.",
    }
