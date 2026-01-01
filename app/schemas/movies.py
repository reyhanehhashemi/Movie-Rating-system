from typing import List, Optional, Literal

from pydantic import BaseModel, conint, Field


# -------------------------
#  Director & Genre Outputs
# -------------------------

class DirectorOut(BaseModel):
    """Director information returned in movie responses."""
    id: int
    name: str
    # در داک برای جزئیات فیلم birth_year و description هم آمده‌اند
    birth_year: Optional[int] = None
    description: Optional[str] = None

    class Config:
        from_attributes = True


class GenreOut(BaseModel):
    """
    Genre model (فعلاً برای استفاده داخلی/احتمالی؛
    در خروجی نهایی فقط name ژانرها به‌صورت str برگردانده می‌شود).
    """
    id: int
    name: str

    class Config:
        from_attributes = True


# -------------------------
#  Movie Outputs (List / Detail)
# -------------------------

class MovieListItem(BaseModel):
    """
    Single movie item in list endpoint.

    مطابق داک:
    - id
    - title
    - release_year
    - director (id, name)
    - genres: ["Drama", "Crime", ...]
    - average_rating
    - ratings_count
    """
    id: int
    title: str
    release_year: int
    director: DirectorOut
    genres: List[str]
    average_rating: Optional[float] = None
    ratings_count: int = 0

    class Config:
        from_attributes = True


class MovieDetail(BaseModel):
    """
    Detailed movie info for GET /api/v1/movies/{movie_id}

    مطابق داک:
    - id
    - title
    - release_year
    - cast
    - director (با جزئیات بیشتر)
    - genres: ["Drama", "Crime", ...]
    - average_rating
    - ratings_count
    """
    id: int
    title: str
    release_year: int
    cast: Optional[str] = None
    director: DirectorOut
    genres: List[str]
    average_rating: Optional[float] = None
    ratings_count: int = 0

    class Config:
        from_attributes = True


class MovieListPage(BaseModel):
    """
    Paginated movie list response.

    داک این فیلدها را مثال زده:
    - page
    - page_size
    - total_items
    - items
    """
    page: int
    page_size: int
    total_items: int
    # داشتن pages اضافی مشکلی ندارد و به کلاینت کمک می‌کند
    pages: int
    items: List[MovieListItem]


# -------------------------
#  Movie Inputs (Create / Update)
# -------------------------

class MovieCreate(BaseModel):
    """
    Request body برای ساخت فیلم جدید (POST /api/v1/movies/)

    نکات داک:
    - title اجباری و نباید خالی باشد
    - director_id باید به کارگردان معتبر اشاره کند
    - release_year باید معتبر باشد
    - genre_ids باید شناسه‌های ژانرهای معتبر باشند
    """
    title: str = Field(min_length=1)
    director_id: int
    release_year: int
    cast: Optional[str] = None
    genre_ids: List[int]


class MovieUpdate(BaseModel):
    """
    Request body برای به‌روزرسانی فیلم (PUT /api/v1/movies/{movie_id})

    این مدل را به‌صورت partial در نظر گرفتیم:
    - هر فیلدی که ارسال نشود، دست‌نخورده می‌ماند.
    - اگر title ارسال شود، نباید خالی باشد (مطابق قاعده‌ی ساخت).
    """
    title: Optional[str] = Field(None, min_length=1)
    director_id: Optional[int] = None
    release_year: Optional[int] = None
    cast: Optional[str] = None
    genre_ids: Optional[List[int]] = None


# -------------------------
#  Rating Input / Output
# -------------------------

class MovieRatingCreate(BaseModel):
    """
    Request body برای ثبت امتیاز فیلم
    (POST /api/v1/movies/{movie_id}/ratings)

    مطابق داک: امتیاز باید عدد صحیح بین ۱ تا ۱۰ باشد.
    """
    score: conint(ge=1, le=10)


class RatingOut(BaseModel):
    """
    مطابق نمونه‌ی داک برای پاسخ ثبت امتیاز:

    {
      "status": "success",
      "data": {
        "rating_id": 555,
        "movie_id": 42,
        "score": 8,
        "created_at": "2025-10-29T10:30:00Z"
      }
    }
    """
    rating_id: int
    movie_id: int
    score: int
    created_at: str  # ISO datetime به‌صورت رشته

    class Config:
        from_attributes = True


# -------------------------
#  Response Envelopes (status / data / error)
# -------------------------

class SuccessMovieListResponse(BaseModel):
    status: Literal["success"]
    data: MovieListPage


class SuccessMovieDetailResponse(BaseModel):
    status: Literal["success"]
    data: MovieDetail


class SuccessRatingResponse(BaseModel):
    status: Literal["success"]
    data: RatingOut


class ErrorInfo(BaseModel):
    code: int
    message: str


class ErrorResponse(BaseModel):
    status: Literal["failure"]
    error: ErrorInfo
