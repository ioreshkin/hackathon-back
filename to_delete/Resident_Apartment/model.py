from sqlalchemy import Column, Integer, ForeignKey, UniqueConstraint
from to_delete.database import Base
from sqlalchemy.orm import relationship

class Resident_Apartment(Base):
    __tablename__ = 'resident_apartment'

    id = Column(Integer, primary_key=True)
    resident_id = Column(Integer, ForeignKey('resident.id', ondelete='CASCADE'), nullable=False)
    apartment_id = Column(Integer, ForeignKey('apartment.id', ondelete='CASCADE'), nullable=False)

    __table_args__ = (
        UniqueConstraint('resident_id', 'apartment_id', name='uq_resident_apartment'),
    )

    resident = relationship(
        'Resident',
        back_populates='apartments'
    )

    apartment = relationship(
        'Apartment',
        back_populates='residents'
    )