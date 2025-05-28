from datetime import date
from typing import TYPE_CHECKING

from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from app.db.models.reel import Reel


class Movie(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    title: str
    description: str | None = None
    author: int = Field(foreign_key="user.uidd")  # Foreign key to User model
    type: str | None = None  # type of file (e.g. "mp4", "avi")
    duration: int | None = None  # duration in seconds
    native_lang: str | None = None  # language of the movie
    file_path: str | None = None  # Path to the movie file
    thumbnail_path: str | None = None  # Path to the poster image
    created_at: date = Field(default_factory=date.today)
    reels: list["Reel"] = Relationship(back_populates="movie")
