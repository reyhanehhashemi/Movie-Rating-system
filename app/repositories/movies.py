from typing import List, Optional, Tuple, Dict

from sqlalchemy import func
from sqlalchemy.orm import Session, selectinload

from app.models.movie import Movie
from app.models.genre import Genre
from app.models.movie_rating import MovieRating
from app.exceptions.app_exceptions import ValidationException


def _load_and_validate_genres(
    db: Session,
    genre_ids: Optional[List[int]],
) -> List[Genre]:
    """
    همه‌ی genre_ids را از دیتابیس می‌خواند و اگر حتی
    یک id نامعتبر بود، ValidationException می‌اندازد.

    اگر genre_ids خالی یا None باشد، لیست خالی برمی‌گرداند.
    """
    if not genre_ids:
        return []

    # برای مقایسه تعداد، فقط idهای یکتا مهم هستند
    unique_ids = list(set(genre_ids))

    genres = (
        db.query(Genre)
        .filter(Genre.id.in_(unique_ids))
        .all()
    )

    if len(genres) != len(unique_ids):
        # حداقل یک genre_id نامعتبر است
        raise ValidationException("Invalid director_id or genres")

    return genres


def get_movies(
    db: Session,
    page: int,
    page_size: int,
    title: Optional[str] = None,
    release_year: Optional[int] = None,
    genre_name: Optional[str] = None,
) -> Tuple[List[Movie], int, Dict[int, Tuple[Optional[float], int]]]:
    """
    برمی‌گرداند:
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


def create_movie(
    db: Session,
    title: str,
    director_id: int,
    release_year: int,
    cast: Optional[str],
    genre_ids: Optional[List[int]] = None,
) -> Movie:
    """
    ساخت فیلم جدید. اگر director_id نامعتبر باشد، دیتابیس
    IntegrityError می‌دهد (در لایه‌ی بالاتر هندل می‌شود).
    اگر genre_ids شامل شناسه‌ی نامعتبر باشد، ValidationException می‌اندازیم.
    """
    movie = Movie(
        title=title,
        director_id=director_id,
        release_year=release_year,
        cast=cast,
    )

    if genre_ids is not None:
        genres = _load_and_validate_genres(db, genre_ids)
        movie.genres = genres

    db.add(movie)
    db.commit()
    db.refresh(movie)
    return movie


def update_movie(
    db: Session,
    movie_id: int,
    title: Optional[str] = None,
    director_id: Optional[int] = None,
    release_year: Optional[int] = None,
    cast: Optional[str] = None,
    genre_ids: Optional[List[int]] = None,
) -> Optional[Movie]:
    """
    به‌روزرسانی فیلم.

    - اگر فیلم وجود نداشته باشد → None برمی‌گرداند.
    - اگر director_id نامعتبر باشد → دیتابیس IntegrityError می‌دهد.
    - اگر genre_ids داده شود و شامل شناسه‌ی نامعتبر باشد →
      ValidationException.
    """
    movie = db.query(Movie).filter(Movie.id == movie_id).first()
    if not movie:
        return None

    if title is not None:
        movie.title = title
    if director_id is not None:
        movie.director_id = director_id
    if release_year is not None:
        movie.release_year = release_year
    if cast is not None:
        movie.cast = cast

    if genre_ids is not None:
        genres = _load_and_validate_genres(db, genre_ids)
        movie.genres = genres

    db.commit()
    db.refresh(movie)
    return movie


def delete_movie(db: Session, movie_id: int) -> bool:
    movie = db.query(Movie).filter(Movie.id == movie_id).first()
    if not movie:
        return False

    db.delete(movie)
    db.commit()
    return True


def add_movie_rating(
    db: Session,
    movie_id: int,
    score: int,
) -> Optional[MovieRating]:
    movie = db.query(Movie).filter(Movie.id == movie_id).first()
    if not movie:
        return None

    rating = MovieRating(movie_id=movie_id, score=score)
    db.add(rating)
    db.commit()
    db.refresh(rating)
    return rating
