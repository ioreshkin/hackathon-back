from sqlalchemy import Column, Integer, String
from to_delete.database import Base
from sqlalchemy.orm import relationship

class Home(Base):
    __tablename__ = 'home'

    id = Column(Integer, primary_key=True)
    street = Column(String, nullable=True)

    zhk_homes = relationship(
        'ZHK_Home',
        back_populates='home'

    )

    home_apartments = relationship(
        'Home_Apartment',
        back_populates='home'
    )

