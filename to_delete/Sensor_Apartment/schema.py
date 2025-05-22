from pydantic import BaseModel

class SensorApartmentBase(BaseModel):
    sensor_id: int
    apartment_id: int

    class Config:
        from_attributes = True

class SensorApartmentCreate(SensorApartmentBase):
    id: int
