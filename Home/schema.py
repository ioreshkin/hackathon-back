from pydantic import BaseModel
from typing import Optional

class HomeBase(BaseModel):
    id: int
    coordinates: Optional[str] = None

    class Config:
        from_attributes = True

class HomeCreate(HomeBase):
    id: int
