from pydantic import BaseModel
from typing import Optional

class ApartmentBase(BaseModel):
    id: int
    number: int
    link: Optional[str] = None

    class Config:
        from_attributes = True

class ApartmentCreate(ApartmentBase):
    id: int