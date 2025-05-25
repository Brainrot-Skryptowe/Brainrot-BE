from datetime import date

from sqlmodel import Field, SQLModel


class Reel(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    title: str
    description: str | None = None
    duration: int | None = None
    poster_path: str | None = None
    file_path: str | None = None
    created_at: date = Field(default_factory=date.today)
