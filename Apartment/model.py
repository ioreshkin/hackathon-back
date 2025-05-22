from sqlalchemy import Column, Integer, String
from database import Base
from sqlalchemy.orm import relationship

class Apartment(Base):
    __tablename__ = 'apartment'

    id = Column(Integer, primary_key=True)
    number = Column(Integer)
    link = Column(String, nullable=False)

    home_apartments = relationship(
        'Home_Apartment',
        back_populates='apartment'
    )

    residents = relationship(
        'Resident_Apartment',
        back_populates='apartment',
        cascade='all, delete-orphan'
    )

    sensors = relationship(
        'Sensor_Apartment',
        back_populates='apartment'
        )