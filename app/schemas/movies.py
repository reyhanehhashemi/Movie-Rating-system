from typing import List, Optional

from pydantic import BaseModel


class DirectorOut(BaseModel):
    id: int
    name: str

    class Config:
        from_attributes = True


class GenreOut(BaseModel):
    id: int
    name: str

    class Config:
        from_attributes = True


class MovieListItem(BaseModel):
    id: int
    title: str
    release_year: int
    director: DirectorOut
    genres: List[GenreOut]
    average_rating: Optional[float] = None
    ratings_count: int = 0

    class Config:
        from_attributes = True


class MovieDetail(BaseModel):
    id: int
    title: str
    release_year: int
    cast: Optional[str] = None
    director: DirectorOut
    genres: List[GenreOut]
    average_rating: Optional[float] = None
    ratings_count: int = 0

    class Config:
        from_attributes = True


class MovieListPage(BaseModel):
    page: int
    page_size: int
    total: int
    pages: int
    items: List[MovieListItem]
