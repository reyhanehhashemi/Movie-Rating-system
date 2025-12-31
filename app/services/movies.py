from math import ceil
from typing import Optional

from sqlalchemy.orm import Session

from app.repositories.movies import get_movies, get_movie_by_id
from app.schemas.movies import MovieListPage, MovieListItem, MovieDetail


def list_movies_service(
    db: Session,
    page: int,
    page_size: int,
    title: Optional[str] = None,
    release_year: Optional[int] = None,
    genre: Optional[str] = None,
) -> MovieListPage:
    movies, total, stats = get_movies(
        db=db,
        page=page,
        page_size=page_size,
        title=title,
        release_year=release_year,
        genre_name=genre,
    )

    pages = ceil(total / page_size) if total > 0 else 0

    items: list[MovieListItem] = []

    for m in movies:
        avg_rating, cnt = stats.get(m.id, (None, 0))

        item = MovieListItem(
            id=m.id,
            title=m.title,
            release_year=m.release_year,
            director=m.director,
            genres=list(m.genres),
            average_rating=avg_rating,
            ratings_count=cnt,
        )
        items.append(item)

    return MovieListPage(
        page=page,
        page_size=page_size,
        total=total,
        pages=pages,
        items=items,
    )


def get_movie_detail_service(
    db: Session,
    movie_id: int,
) -> Optional[MovieDetail]:
    movie, avg_rating, cnt = get_movie_by_id(db=db, movie_id=movie_id)

    if not movie:
        return None

    return MovieDetail(
        id=movie.id,
        title=movie.title,
        release_year=movie.release_year,
        cast=movie.cast,
        director=movie.director,
        genres=list(movie.genres),
        average_rating=avg_rating,
        ratings_count=cnt,
    )
