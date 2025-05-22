from pydantic import BaseModel
from typing import Optional

class ResidentBase(BaseModel):
    id: int
    name: Optional[str] = None

    class Config:
        from_attributes = True

class ResidentCreate(ResidentBase):
    id: int