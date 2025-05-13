from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import date

class Movie(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str
    description: Optional[str] = None
    type: Optional[str] = None  # type of file (e.g. "mp4", "avi")
    duration: Optional[int] = None  # duration in seconds
    file_path: Optional[str] = None  # Path to the movie file
    poster_path: Optional[str] = None  # Path to the poster image
    created_at: date = Field(default_factory=date.today)