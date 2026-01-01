from math import ceil
from typing import Optional, List

from sqlalchemy.orm import Session

from app.models.movie_rating import MovieRating
from app.repositories.movies import (
    get_movies,
    get_movie_by_id,
    create_movie,
    update_movie,
    delete_movie,
    add_movie_rating,
)
from app.schemas.movies import (
    MovieListPage,
    MovieListItem,
    MovieDetail,
    MovieCreate,
    MovieUpdate,
)


def list_movies_service(
    db: Session,
    page: int,
    page_size: int,
    title: Optional[str] = None,
    release_year: Optional[int] = None,
    genre: Optional[str] = None,
) -> MovieListPage:
    """
    سرویس لیست فیلم‌ها با پشتیبانی از:
    - pagination
    - فیلتر بر اساس title, release_year, genre (نام ژانر)
    """
    movies, total, stats = get_movies(
        db=db,
        page=page,
        page_size=page_size,
        title=title,
        release_year=release_year,
        genre_name=genre,
    )

    pages = ceil(total / page_size) if total > 0 else 0

    items: List[MovieListItem] = []

    for m in movies:
        avg_rating, cnt = stats.get(m.id, (None, 0))

        item = MovieListItem(
            id=m.id,
            title=m.title,
            release_year=m.release_year,
            director=m.director,
            # ژانرها به صورت لیست str مطابق داک
            genres=[g.name for g in m.genres],
            average_rating=avg_rating,
            ratings_count=cnt,
        )
        items.append(item)

    return MovieListPage(
        page=page,
        page_size=page_size,
        total_items=total,
        pages=pages,
        items=items,
    )


def get_movie_detail_service(
    db: Session,
    movie_id: int,
) -> Optional[MovieDetail]:
    """
    سرویس دریافت جزئیات یک فیلم تکی.
    """
    movie, avg_rating, cnt = get_movie_by_id(db=db, movie_id=movie_id)

    if not movie:
        return None

    return MovieDetail(
        id=movie.id,
        title=movie.title,
        release_year=movie.release_year,
        cast=movie.cast,
        director=movie.director,
        genres=[g.name for g in movie.genres],
        average_rating=avg_rating,
        ratings_count=cnt,
    )


def create_movie_service(
    db: Session,
    movie_in: MovieCreate,
):
    """
    سرویس ایجاد فیلم جدید.

    - در صورت موفقیت، آبجکت Movie را برمی‌گرداند
      (کنترلر MovieDetail و envelope را می‌سازد).
    """
    movie = create_movie(
        db=db,
        title=movie_in.title,
        director_id=movie_in.director_id,
        release_year=movie_in.release_year,
        cast=movie_in.cast,
        genre_ids=movie_in.genre_ids,
    )
    return movie


def update_movie_service(
    db: Session,
    movie_id: int,
    movie_in: MovieUpdate,
) -> Optional[MovieDetail]:
    """
    سرویس به‌روزرسانی فیلم.

    - اگر فیلم وجود نداشته باشد، None برمی‌گرداند.
    - در غیر این صورت MovieDetail با امتیازهای به‌روز برمی‌گرداند.
    """
    movie = update_movie(
        db=db,
        movie_id=movie_id,
        title=movie_in.title,
        director_id=movie_in.director_id,
        release_year=movie_in.release_year,
        cast=movie_in.cast,
        genre_ids=movie_in.genre_ids,
    )

    if not movie:
        return None

    # آمار امتیاز را از نو بخوانیم
    _, avg_rating, cnt = get_movie_by_id(db=db, movie_id=movie_id)

    return MovieDetail(
        id=movie.id,
        title=movie.title,
        release_year=movie.release_year,
        cast=movie.cast,
        director=movie.director,
        genres=[g.name for g in movie.genres],
        average_rating=avg_rating,
        ratings_count=cnt,
    )


def delete_movie_service(
    db: Session,
    movie_id: int,
) -> bool:
    """
    سرویس حذف فیلم.
    """
    return delete_movie(db=db, movie_id=movie_id)


def add_movie_rating_service(
    db: Session,
    movie_id: int,
    score: int,
) -> Optional[MovieRating]:
    """
    سرویس ثبت امتیاز برای یک فیلم.

    - اگر فیلم وجود نداشته باشد، None.
    - در غیر این صورت MovieRating برمی‌گرداند
      (کنترلر RatingOut و envelope را می‌سازد).
    """
    rating = add_movie_rating(db=db, movie_id=movie_id, score=score)
    return rating
