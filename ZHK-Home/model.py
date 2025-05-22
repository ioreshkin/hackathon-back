from sqlalchemy import Column, Integer, ForeignKey, UniqueConstraint
from database import Base
from sqlalchemy.orm import relationship

class ZHK_Home(Base):
    __tablename__ = 'zhk_home'

    id = Column(Integer, primary_key=True)
    zhk_id = Column(Integer, ForeignKey('zhk.id', ondelete='CASCADE'), nullable=False)
    home_id = Column(Integer, ForeignKey('home.id', ondelete='CASCADE'), nullable=False)

    __table_args__ = (
        UniqueConstraint('zhk_id', 'home_id', name='uq_zhk_home_pair'),
    )

    zhk = relationship('ZHK', back_populates='zhk_homes')
    home = relationship('Home', back_populates='zhk_homes')
