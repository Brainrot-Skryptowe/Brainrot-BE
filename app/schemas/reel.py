from datetime import date

from pydantic import BaseModel

from app.schemas.audio import AudioRead


class ReelBase(BaseModel):
    file_path: str | None = None


class ReelRead(ReelBase):
    id: int
    created_at: date

    class Config:
        from_attributes = True


class ReelCreate(BaseModel):
    movie_id: int
    audio_id: int | None
    include_srt: bool = False


class ReelWithAudio(BaseModel):
    id: int
    lang: str
    file_path: str | None
    movie_id: int
    author: int
    audio: AudioRead | None

    class Config:
        from_attributes = True
