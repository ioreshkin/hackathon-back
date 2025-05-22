from sqlalchemy import Column, Integer, String
from database import Base
from sqlalchemy.orm import relationship

class Sensor(Base):
    __tablename__ = 'sensor'

    id = Column(Integer, primary_key=True)
    type = Column(String, nullable=False)
    coordinates = Column(String, nullable=True)

    apartments = relationship(
        'Sensor_Apartment',
        back_populates='sensor'
    )

    observations = relationship(
        'Observation',
        back_populates='sensor'
    )