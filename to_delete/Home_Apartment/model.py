from sqlalchemy import Column, Integer, ForeignKey, UniqueConstraint
from to_delete.database import Base
from sqlalchemy.orm import relationship

class Home_Apartment(Base):
    __tablename__ = 'home_apartment'

    id = Column(Integer, primary_key=True)
    home_id = Column(Integer, ForeignKey('home.id', ondelete='CASCADE'), nullable=False)
    apartment_id = Column(Integer, ForeignKey('apartment.id', ondelete='CASCADE'), nullable=False)

    __table_args__ = (
        UniqueConstraint('home_id', 'apartment_id', name='uq_home_apartment_pair'),
    )

    home = relationship(
        'Home',
        back_populates='home_apartments'
    )

    apartment = relationship(
        'Apartment',
        back_populates='home_apartments'
    )
