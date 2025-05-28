from datetime import date
from typing import TYPE_CHECKING, Optional

from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from app.db.models.audio import Audio


class Srt(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    audio_id: int = Field(foreign_key="audio.id")
    file_path: str
    created_at: date = Field(default_factory=date.today)

    audio: Optional["Audio"] = Relationship(back_populates="srt")
