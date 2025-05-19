from datetime import date

from sqlmodel import Field, SQLModel


class Audio(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    title: str
    text: str
    voice: int
    language: str
    speed: float
    file_path: str | None = None
    created_at: date = Field(default_factory=date.today)
