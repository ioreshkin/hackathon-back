from datetime import datetime
from pydantic import BaseModel
from typing import Optional

class ObservationBase(BaseModel):
    id: int
    sensor_id: int
    timestamp: Optional[datetime]
    temperature: Optional[float]
    humidity: Optional[float]
    co2_level: Optional[float]
    phenomenon_id: Optional[int]

    class Config:
        from_attributes = True

class ObservationCreate(ObservationBase):
    id: int