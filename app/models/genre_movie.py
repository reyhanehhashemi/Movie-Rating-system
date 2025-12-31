from sqlalchemy import Column, Integer, ForeignKey, UniqueConstraint

from app.db.session import Base


class GenreMovie(Base):
    __tablename__ = "genres_movie"

    movie_id = Column(
        Integer,
        ForeignKey("movies.id", ondelete="CASCADE"),
        primary_key=True,
    )
    genre_id = Column(
        Integer,
        ForeignKey("genres.id", ondelete="CASCADE"),
        primary_key=True,
    )

    __table_args__ = (
        UniqueConstraint("movie_id", "genre_id", name="uq_movie_genre"),
    )
