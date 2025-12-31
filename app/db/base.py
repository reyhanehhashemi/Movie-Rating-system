from app.db.session import Base


from app.models.director import Director  # noqa
from app.models.genre import Genre  # noqa
from app.models.genre_movie import GenreMovie  # noqa
from app.models.movie import Movie  # noqa
from app.models.movie_rating import MovieRating  # noqa

__all__ = [
    "Base",
    "Director",
    "Genre",
    "GenreMovie",
    "Movie",
    "MovieRating",
]
