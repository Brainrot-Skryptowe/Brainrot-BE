from datetime import date
from typing import TYPE_CHECKING, Optional

from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from app.db.models.audio import Audio
    from app.db.models.movie import Movie


class Reel(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    movie_id: int = Field(foreign_key="movie.id")
    lang: str
    author: int = Field(foreign_key="user.uidd")
    file_path: str | None = None
    audio_id: int | None = Field(default=None, foreign_key="audio.id")
    created_at: date = Field(default_factory=date.today)

    movie: Optional["Movie"] = Relationship(back_populates="reels")
    audio: Optional["Audio"] = Relationship(back_populates="reel")
