from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.db.deps import get_db
from app.schemas.movies import MovieListPage, MovieDetail
from app.services.movies import list_movies_service, get_movie_detail_service

router = APIRouter(prefix="/api/v1/movies", tags=["movies"])


@router.get("/", response_model=MovieListPage)
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
    return list_movies_service(
        db=db,
        page=page,
        page_size=page_size,
        title=title,
        release_year=release_year,
        genre=genre,
    )


@router.get("/{movie_id}", response_model=MovieDetail)
def get_movie(
    movie_id: int,
    db: Session = Depends(get_db),
):
    movie = get_movie_detail_service(db=db, movie_id=movie_id)
    if not movie:
        raise HTTPException(status_code=404, detail="Movie not found")
    return movie
