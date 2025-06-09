from datetime import date

from pydantic import BaseModel


class MusicBase(BaseModel):
    title: str


class MusicRead(MusicBase):
    id: int
    created_at: date
    author: int
    type: str | None = None
    duration: int | None = None
    file_path: str | None = None

    class Config:
        orm_mode = True


class MusicCreate(MusicBase):
    class Config:
        orm_mode = True
