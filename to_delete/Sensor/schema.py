from pydantic import BaseModel
from typing import Optional

class SensorBase(BaseModel):
    type: str
    coordinates: Optional[str] = None

    class Config:
        from_attributes = True

class SensorCreate(SensorBase):
    id: int
