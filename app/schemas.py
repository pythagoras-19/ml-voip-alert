from pydantic import BaseModel
from typing import Dict, Any, List, Optional


class ScoreRequest(BaseModel):
    patient_ref_token: str
    features: Dict[str, Any]


class Factor(BaseModel):
    feature: str
    impact: float


class ScoreResponse(BaseModel):
    risk: float
    top_factors: List[Factor]
    alerted: bool
    alert_id: Optional[str] = None


class AlertData(BaseModel):
    alert_id: str
    patient_token: str
    risk: float
    top_factors: List[Factor]
    timestamp: str
