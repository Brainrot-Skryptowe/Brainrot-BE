from datetime import date

from pydantic import BaseModel


class MovieBase(BaseModel):
    title: str
    description: str | None = None
    type: str | None = None
    duration: int | None = None
    file_path: str | None = None
    poster_path: str | None = None


class MovieRead(MovieBase):
    id: int
    created_at: date

    class Config:
        orm_mode = True
