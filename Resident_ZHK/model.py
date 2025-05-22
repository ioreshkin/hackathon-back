from sqlalchemy import Column, Integer, ForeignKey, UniqueConstraint
from database import Base
from sqlalchemy.orm import relationship

class Resident_ZHK(Base):
    __tablename__ = 'resident_zhk'

    id = Column(Integer, primary_key=True)
    resident_id = Column(Integer, ForeignKey('resident.id', ondelete='CASCADE'), nullable=False)
    zhk_id = Column(Integer, ForeignKey('zhk.id', ondelete='CASCADE'), nullable=False)

    __table_args__ = (
        UniqueConstraint('resident_id', 'zhk_id', name='uq_resident_zhk'),
    )

    resident = relationship(
        'Resident',
        back_populates='zhks'
    )

    zhk = relationship(
        'ZHK',
        back_populates='residents'
    )