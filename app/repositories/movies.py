from typing import List, Optional, Tuple, Dict

from sqlalchemy import func
from sqlalchemy.orm import Session, selectinload

from app.models.movie import Movie
from app.models.genre import Genre
from app.models.movie_rating import MovieRating


def get_movies(
    db: Session,
    page: int,
    page_size: int,
    title: Optional[str] = None,
    release_year: Optional[int] = None,
    genre_name: Optional[str] = None,
) -> Tuple[List[Movie], int, Dict[int, Tuple[Optional[float], int]]]:
    """
    برمی‌گردونه:
    - لیست فیلم‌های این صفحه
    - total تعداد کل ردیف‌ها
    - دیکشنری آمار امتیازدهی برای هر فیلم:
      stats[movie_id] = (average_rating, ratings_count)
    """

    query = (
        db.query(Movie)
        .options(
            selectinload(Movie.director),
            selectinload(Movie.genres),
        )
    )

    if title:
        query = query.filter(Movie.title.ilike(f"%{title}%"))

    if release_year:
        query = query.filter(Movie.release_year == release_year)

    if genre_name:
        # join روی Genre برای فیلتر ژانر
        query = query.join(Movie.genres).filter(Genre.name.ilike(f"%{genre_name}%"))

    query = query.distinct()

    total = query.count()

    # pagination
    query = query.order_by(Movie.id).offset((page - 1) * page_size).limit(page_size)

    movies: List[Movie] = query.all()

    # محاسبه average_rating و تعداد امتیازها برای همین فیلم‌های صفحه
    stats: Dict[int, Tuple[Optional[float], int]] = {}

    if movies:
        movie_ids = [m.id for m in movies]

        rating_rows = (
            db.query(
                MovieRating.movie_id,
                func.avg(MovieRating.score).label("avg_score"),
                func.count(MovieRating.id).label("cnt"),
            )
            .filter(MovieRating.movie_id.in_(movie_ids))
            .group_by(MovieRating.movie_id)
            .all()
        )

        for row in rating_rows:
            stats[row.movie_id] = (float(row.avg_score), row.cnt)

    return movies, total, stats


def get_movie_by_id(
    db: Session,
    movie_id: int,
) -> Tuple[Optional[Movie], Optional[float], int]:
    """
    یک فیلم و آمار امتیازدهی‌اش را برمی‌گرداند.
    """
    movie: Optional[Movie] = (
        db.query(Movie)
        .options(
            selectinload(Movie.director),
            selectinload(Movie.genres),
            selectinload(Movie.ratings),
        )
        .filter(Movie.id == movie_id)
        .first()
    )

    if not movie:
        return None, None, 0

    rating_row = (
        db.query(
            func.avg(MovieRating.score).label("avg_score"),
            func.count(MovieRating.id).label("cnt"),
        )
        .filter(MovieRating.movie_id == movie_id)
        .first()
    )

    avg_score: Optional[float] = None
    cnt = 0

    if rating_row and rating_row.cnt:
        avg_score = float(rating_row.avg_score)
        cnt = rating_row.cnt

    return movie, avg_score, cnt
