from sqlalchemy import Column, Integer, String
from database import Base
from sqlalchemy.orm import relationship

class Resident(Base):
    __tablename__ = 'resident'

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)

    apartments = relationship(
        'Resident_Apartment',
        back_populates='resident')

    zhks = relationship(
        'Resident_ZHK',
        back_populates='resident'
    )
