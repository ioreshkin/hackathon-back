from pydantic import BaseModel
from typing import Optional

class ZHKBase(BaseModel):
    id: int
    name: Optional[str] = None

    class Config:
        orm_mode = True

class ZHKCreate(ZHKBase):
    id: int