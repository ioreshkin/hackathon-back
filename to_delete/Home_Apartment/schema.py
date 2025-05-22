from pydantic import BaseModel
from typing import Optional

class ResidentApartmentBase(BaseModel):
    id: int
    resident_id: int
    apartment_id: int

    class Config:
        from_attributes = True

class ResidentApartmentCreate(ResidentApartmentBase):
    id: int

