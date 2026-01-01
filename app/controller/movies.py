# app/controller/movies.py
from typing import Optional

from fastapi import APIRouter, Depends, Query, status
from fastapi.responses import JSONResponse, Response
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.logging_config import logger
from app.db.deps import get_db
from app.schemas.movies import (
    MovieListPage,
    MovieDetail,
    MovieCreate,
    MovieUpdate,
    MovieRatingCreate,
    SuccessMovieListResponse,
    SuccessMovieDetailResponse,
    SuccessRatingResponse,
    RatingOut,
)
from app.services.movies import (
    list_movies_service,
    get_movie_detail_service,
    create_movie_service,
    update_movie_service,
    delete_movie_service,
    add_movie_rating_service,
)

router = APIRouter(prefix="/api/v1/movies", tags=["movies"])


def error_response(status_code: int, message: str) -> JSONResponse:
    """
    ساخت پاسخ خطا مطابق داک:

    {
      "status": "failure",
      "error": {
        "code": <HTTP_STATUS>,
        "message": "<error_message>"
      }
    }
    """
    return JSONResponse(
        status_code=status_code,
        content={
            "status": "failure",
            "error": {
                "code": status_code,
                "message": message,
            },
        },
    )


@router.get(
    "/",
    response_model=SuccessMovieListResponse,
)
def list_movies(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    title: Optional[str] = None,
    release_year: Optional[int] = None,
    genre: Optional[str] = None,
    db: Session = Depends(get_db),
):
    """
    لیست فیلم‌ها با pagination و فیلترها:
    - title: جست‌وجوی جزئی در عنوان
    - release_year: سال انتشار
    - genre: نام ژانر (مثلاً Action)
    """
    route_path = "/api/v1/movies/"

    # شروع عملیات
    logger.info(
        "Listing movies",
        extra={
            "route": route_path,
            "page": page,
            "page_size": page_size,
            "title": title,
            "release_year": release_year,
            "genre": genre,
        },
    )

    try:
        page_data: MovieListPage = list_movies_service(
            db=db,
            page=page,
            page_size=page_size,
            title=title,
            release_year=release_year,
            genre=genre,
        )
    except Exception:
        logger.error(
            "Failed to list movies",
            extra={
                "route": route_path,
                "page": page,
                "page_size": page_size,
                "title": title,
                "release_year": release_year,
                "genre": genre,
            },
            exc_info=True,
        )
        return error_response(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message="Internal server error",
        )

    logger.info(
        "Movies listed successfully",
        extra={
            "route": route_path,
            "page": page,
            "page_size": page_size,
            "total_items": page_data.total_items,
            "pages": page_data.pages,
        },
    )

    return SuccessMovieListResponse(
        status="success",
        data=page_data,
    )


@router.get(
    "/{movie_id}",
    response_model=SuccessMovieDetailResponse,
)
def get_movie(
    movie_id: int,
    db: Session = Depends(get_db),
):
    """
    مشاهده‌ی جزئیات یک فیلم.

    - در صورت موفقیت: status=success + data (MovieDetail)
    - در صورت عدم وجود فیلم: 404 با status=failure
    """
    movie: Optional[MovieDetail] = get_movie_detail_service(db=db, movie_id=movie_id)
    if not movie:
        return error_response(
            status_code=status.HTTP_404_NOT_FOUND,
            message="Movie not found",
        )

    return SuccessMovieDetailResponse(
        status="success",
        data=movie,
    )


@router.post(
    "/",
    response_model=SuccessMovieDetailResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_movie(
    movie_in: MovieCreate,
    db: Session = Depends(get_db),
):
    """
    ایجاد فیلم جدید به همراه ژانرها.
    """
    try:
        movie_db = create_movie_service(db=db, movie_in=movie_in)
        movie_detail = MovieDetail(
            id=movie_db.id,
            title=movie_db.title,
            release_year=movie_db.release_year,
            cast=movie_db.cast,
            director=movie_db.director,
            genres=[g.name for g in movie_db.genres],
            average_rating=None,
            ratings_count=0,
        )
        return SuccessMovieDetailResponse(
            status="success",
            data=movie_detail,
        )
    except IntegrityError:
        db.rollback()
        return error_response(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            message="Invalid director_id or genres",
        )


@router.put(
    "/{movie_id}",
    response_model=SuccessMovieDetailResponse,
)
def update_movie(
    movie_id: int,
    movie_in: MovieUpdate,
    db: Session = Depends(get_db),
):
    """
    به‌روزرسانی اطلاعات فیلم.
    """
    try:
        movie_detail = update_movie_service(db=db, movie_id=movie_id, movie_in=movie_in)
    except IntegrityError:
        db.rollback()
        return error_response(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            message="Invalid director_id or genres",
        )

    if not movie_detail:
        return error_response(
            status_code=status.HTTP_404_NOT_FOUND,
            message="Movie not found",
        )

    return SuccessMovieDetailResponse(
        status="success",
        data=movie_detail,
    )


@router.delete(
    "/{movie_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_movie(
    movie_id: int,
    db: Session = Depends(get_db),
):
    """
    حذف فیلم.
    """
    ok = delete_movie_service(db=db, movie_id=movie_id)
    if not ok:
        return error_response(
            status_code=status.HTTP_404_NOT_FOUND,
            message="Movie not found",
        )
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post(
    "/{movie_id}/ratings",
    response_model=SuccessRatingResponse,
    status_code=status.HTTP_201_CREATED,
)
def add_rating(
    movie_id: int,
    rating_in: MovieRatingCreate,
    db: Session = Depends(get_db),
):
    """
    ثبت امتیاز برای فیلم (۱ تا ۱۰).

    - در صورت موفقیت: 201 + status=success + داده‌ی rating
    - در صورت نبودن فیلم: 404 با status=failure
    """
    route_path = f"/api/v1/movies/{movie_id}/ratings"

    # شروع عملیات rating
    logger.info(
        "Rating movie",
        extra={
            "route": route_path,
            "movie_id": movie_id,
            "rating": rating_in.score,
        },
    )

    try:
        rating = add_movie_rating_service(
            db=db,
            movie_id=movie_id,
            score=rating_in.score,
        )
    except Exception:
        logger.error(
            "Failed to save rating",
            extra={
                "route": route_path,
                "movie_id": movie_id,
                "rating": rating_in.score,
            },
            exc_info=True,
        )
        return error_response(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message="Internal server error",
        )

    if not rating:
        # یعنی فیلمی با این id وجود ندارد
        logger.warning(
            "Movie not found for rating",
            extra={
                "route": route_path,
                "movie_id": movie_id,
                "rating": rating_in.score,
            },
        )
        return error_response(
            status_code=status.HTTP_404_NOT_FOUND,
            message="Movie not found",
        )

    rating_out = RatingOut(
        rating_id=rating.id,
        movie_id=rating.movie_id,
        score=rating.score,
        created_at=rating.created_at.isoformat(),
    )

    logger.info(
        "Rating saved successfully",
        extra={
            "route": route_path,
            "movie_id": rating.movie_id,
            "rating": rating.score,
            "rating_id": rating.id,
        },
    )

    return SuccessRatingResponse(
        status="success",
        data=rating_out,
    )
