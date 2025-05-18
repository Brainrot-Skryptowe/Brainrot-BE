from datetime import date

from sqlmodel import Field, SQLModel


class Movie(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    title: str
    description: str | None = None
    type: str | None = None  # type of file (e.g. "mp4", "avi")
    duration: int | None = None  # duration in seconds
    file_path: str | None = None  # Path to the movie file
    poster_path: str | None = None  # Path to the poster image
    created_at: date = Field(default_factory=date.today)
