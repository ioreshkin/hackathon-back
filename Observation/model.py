from sqlalchemy import Column, Integer, ForeignKey, DateTime, Float
from database import Base
from sqlalchemy.orm import relationship
from datetime import datetime

class Observation(Base):
    __tablename__ = 'observation'

    id = Column(Integer, primary_key=True)
    sensor_id = Column(Integer, ForeignKey('sensor.id', ondelete='CASCADE'), nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    temperature = Column(Float, nullable=True)
    humidity = Column(Float, nullable=True)
    co2_level = Column(Float, nullable=True)
    phenomenon_id = Column(Integer, ForeignKey('phenomenon.id', ondelete='SET NULL'), nullable=True)

    sensor = relationship(
        'Sensor',
        back_populates='observations'
    )

    phenomenon = relationship(
        'Phenomenon',
        back_populates='observations'
    )