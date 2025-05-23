from datetime import date

from sqlmodel import Field, SQLModel


class Srt(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    audio_id: int = Field(foreign_key="audio.id")
    file_path: str
    created_at: date = Field(default_factory=date.today)
