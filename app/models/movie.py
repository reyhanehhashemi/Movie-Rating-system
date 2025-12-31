from datetime import datetime

from sqlalchemy import (
    Column,
    Integer,
    String,
    ForeignKey,
    DateTime,
)
from sqlalchemy.orm import relationship

from app.db.session import Base


class Movie(Base):
    __tablename__ = "movies"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    director_id = Column(
        Integer,
        ForeignKey("directors.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    release_year = Column(Integer, nullable=False)
    cast = Column(String, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )

    # relationships
    director = relationship("Director", back_populates="movies")
    genres = relationship(
        "Genre",
        secondary="genres_movie",
        back_populates="movies",
    )
    ratings = relationship(
        "MovieRating",
        back_populates="movie",
        cascade="all, delete-orphan",
    )
