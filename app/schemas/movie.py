from datetime import date

from pydantic import BaseModel

from app.schemas.reel import ReelWithAudio


class MovieBase(BaseModel):
    title: str
    description: str | None = None
    native_lang: str | None = None


class MovieReadBasic(MovieBase):
    id: int
    created_at: date
    author: int
    type: str | None = None
    duration: int | None = None
    file_path: str | None = None
    thumbnail_path: str | None = None

    class Config:
        orm_mode = True


class MovieRead(MovieReadBasic):
    reels: list[ReelWithAudio] = []

    class Config:
        orm_mode = True


class MovieCreate(MovieBase):
    class Config:
        orm_mode = True
