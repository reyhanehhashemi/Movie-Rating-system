from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

from app.db.session import Base


class Director(Base):
    __tablename__ = "directors"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    birth_year = Column(Integer, nullable=True)
    description = Column(String, nullable=True)

    # relationships
    movies = relationship("Movie", back_populates="director")
