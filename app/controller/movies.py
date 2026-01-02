# app/controller/movies.py
from typing import Optional

from fastapi import APIRouter, Depends, Query, status
from fastapi.responses import JSONResponse, Response
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.decorators import log_endpoint
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
    پاسخ خطا مطابق داک:
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


# -------------------------
# LIST MOVIES
# -------------------------
@router.get(
    "/",
    response_model=SuccessMovieListResponse,
)
@log_endpoint("list_movies")
def list_movies(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    title: Optional[str] = None,
    release_year: Optional[int] = None,
    genre: Optional[str] = None,
    db: Session = Depends(get_db),
):
    """
    لیست فیلم‌ها با pagination و فیلترها.
    """
    route_path = "/api/v1/movies/"

    # شروع عملیات: context کامل
    logger.info(
        "Listing movies (page=%s, page_size=%s, title=%s, release_year=%s, "
        "genre=%s, route=%s)",
        page,
        page_size,
        title,
        release_year,
        genre,
        route_path,
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
            "Failed to list movies (page=%s, page_size=%s, title=%s, "
            "release_year=%s, genre=%s, route=%s)",
            page,
            page_size,
            title,
            release_year,
            genre,
            route_path,
            exc_info=True,
        )
        return error_response(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message="Internal server error",
        )

    logger.info(
        "Movies listed successfully (page=%s, page_size=%s, total_items=%s, "
        "pages=%s, route=%s)",
        page,
        page_size,
        page_data.total_items,
        page_data.pages,
        route_path,
    )

    return SuccessMovieListResponse(
        status="success",
        data=page_data,
    )


# -------------------------
# GET MOVIE DETAIL
# -------------------------
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
    """
    movie: Optional[MovieDetail] = get_movie_detail_service(db=db, movie_id=movie_id)
    if not movie:
        logger.warning("Movie not found (movie_id=%s, route=%s)", movie_id, "/api/v1/movies/{movie_id}")
        return error_response(
            status_code=status.HTTP_404_NOT_FOUND,
            message="Movie not found",
        )

    logger.info("Movie detail fetched (movie_id=%s)", movie_id)

    return SuccessMovieDetailResponse(
        status="success",
        data=movie,
    )


# -------------------------
# CREATE MOVIE
# -------------------------
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
    except IntegrityError:
        db.rollback()
        logger.error(
            "Failed to create movie due to invalid director/genres "
            "(title=%s, director_id=%s, genre_ids=%s)",
            movie_in.title,
            movie_in.director_id,
            movie_in.genre_ids,
            exc_info=True,
        )
        return error_response(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            message="Invalid director_id or genres",
        )

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

    logger.info("Movie created successfully (movie_id=%s, title=%s)", movie_db.id, movie_db.title)

    return SuccessMovieDetailResponse(
        status="success",
        data=movie_detail,
    )


# -------------------------
# UPDATE MOVIE
# -------------------------
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
        logger.error(
            "Failed to update movie due to invalid director/genres "
            "(movie_id=%s, director_id=%s, genre_ids=%s)",
            movie_id,
            movie_in.director_id,
            movie_in.genre_ids,
            exc_info=True,
        )
        return error_response(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            message="Invalid director_id or genres",
        )

    if not movie_detail:
        logger.warning("Movie not found for update (movie_id=%s)", movie_id)
        return error_response(
            status_code=status.HTTP_404_NOT_FOUND,
            message="Movie not found",
        )

    logger.info("Movie updated successfully (movie_id=%s)", movie_id)

    return SuccessMovieDetailResponse(
        status="success",
        data=movie_detail,
    )


# -------------------------
# DELETE MOVIE
# -------------------------
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
        logger.warning("Movie not found for delete (movie_id=%s)", movie_id)
        return error_response(
            status_code=status.HTTP_404_NOT_FOUND,
            message="Movie not found",
        )

    logger.info("Movie deleted successfully (movie_id=%s)", movie_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


# -------------------------
# ADD RATING
# -------------------------
@router.post(
    "/{movie_id}/ratings",
    response_model=SuccessRatingResponse,
    status_code=status.HTTP_201_CREATED,
)
@log_endpoint("add_rating")
def add_rating(
    movie_id: int,
    rating_in: MovieRatingCreate,
    db: Session = Depends(get_db),
):
    """
    ثبت امتیاز برای فیلم (۱ تا ۱۰).
    """
    route_path = f"/api/v1/movies/{movie_id}/ratings"

    # شروع عملیات rating با context کامل
    logger.info(
        "Rating movie (movie_id=%s, rating=%s, route=%s)",
        movie_id,
        rating_in.score,
        route_path,
    )

    try:
        rating = add_movie_rating_service(
            db=db,
            movie_id=movie_id,
            score=rating_in.score,
        )
    except Exception:
        logger.error(
            "Failed to save rating (movie_id=%s, rating=%s, route=%s)",
            movie_id,
            rating_in.score,
            route_path,
            exc_info=True,
        )
        return error_response(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message="Internal server error",
        )

    if not rating:
        # یعنی فیلمی با این id وجود ندارد
        logger.warning(
            "Movie not found for rating (movie_id=%s, rating=%s, route=%s)",
            movie_id,
            rating_in.score,
            route_path,
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
        "Rating saved successfully (movie_id=%s, rating=%s)",
        rating.movie_id,
        rating.score,
    )

    return SuccessRatingResponse(
        status="success",
        data=rating_out,
    )
