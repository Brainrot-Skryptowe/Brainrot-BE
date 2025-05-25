from datetime import date

from pydantic import BaseModel


class ReelBase(BaseModel):
    title: str
    description: str | None = None
    duration: int | None = None
    file_path: str | None = None
    poster_path: str | None = None


class ReelRead(ReelBase):
    id: int
    created_at: date

    class Config:
        orm_mode = True


class ReelCreate(BaseModel):
    movie_id: int
    audio_id: int | None
    include_srt: bool = False
    reel_info: ReelInfo


class ReelInfo(BaseModel):
    title: str
    description: str | None = None
