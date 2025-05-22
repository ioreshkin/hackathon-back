from pydantic import BaseModel
from typing import Optional

class PhenomenonBase(BaseModel):
    id: int
    name: Optional[str]
    anomaly_threshold: float
    emergency_threshold: float

class PhenomenonCreate(PhenomenonBase):
    id: int