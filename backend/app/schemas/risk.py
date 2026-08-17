from pydantic import BaseModel, Field


class TimePoint(BaseModel):
    t: str
    value: float
    unit: str
    source: str = "open-meteo"
    quality: str = "ok"


class Factor(BaseModel):
    id: str
    label: str
    contribution_pct: int


class RiskCard(BaseModel):
    id: str
    label: str
    severity: str
    score_pct: int = Field(ge=0, le=100)
    confidence_pct: int = Field(ge=0, le=100)
    horizon_hours: int = 72
    factors: list[Factor]
    method: str = "weighted_linear_v1"
    inputs_used: list[str] = []
    missing_inputs: list[str] = []
    sources: list[str] = []
    updated_at: str


class Quant(BaseModel):
    water_saved_liters_min: int | None = None
    water_saved_liters_max: int | None = None
    method: str | None = None
    assumptions: dict = {}


class Prescription(BaseModel):
    id: str
    priority: int
    action: str
    rationale_codes: list[str] = []
    quant: Quant = Quant()
    sdg: list[str] = ["6", "13"]
    locale_ready: bool = True
    confidence_pct: int = 70
    template_id: str | None = None
    slots: dict = {}
    why: str = ""
    when: str = ""
    who: str = "household / farm"
