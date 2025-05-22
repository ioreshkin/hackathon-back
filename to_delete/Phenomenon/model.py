from sqlalchemy import Column, Integer, String, Float
from to_delete.database import Base
from sqlalchemy.orm import relationship

class Phenomenon(Base):
    __tablename__ = 'phenomenon'

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    anomaly_threshold = Column(Float, nullable=False)
    emergency_threshold = Column(Float, nullable=False)

    observations = relationship(
        'Observation',
        back_populates='phenomenon'
    )
