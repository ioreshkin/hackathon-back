from sqlalchemy import Column, Integer, ForeignKey, UniqueConstraint
from database import Base
from sqlalchemy.orm import relationship

class Sensor_Apartment(Base):
    __tablename__ = 'sensor_apartment'

    id = Column(Integer, primary_key=True)
    apartment_id = Column(Integer, ForeignKey('apartment.id', ondelete='CASCADE'), nullable=False)
    sensor_id = Column(Integer, ForeignKey('sensor.id', ondelete='CASCADE'), nullable=False)

    __table_args__ = (
        UniqueConstraint('apartment_id', 'sensor_id', name='uq_apartment_sensor'),
    )

    apartment = relationship(
        'Apartment',
        back_populates='sensors'
    )

    sensor = relationship(
        'Sensor',
        back_populates='apartments'
    )