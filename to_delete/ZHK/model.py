from sqlalchemy import Column, Integer, String
from to_delete.database import Base
from sqlalchemy.orm import relationship

class ZHK(Base):
    __tablename__ = 'zhk'

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)

    zhk_homes = relationship(
        'ZHK_Home',
        back_populates='zhk'
    )

    residents = relationship(
        'Resident_ZHK',
        back_populates='zhk'
    )

