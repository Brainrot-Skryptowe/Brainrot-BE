from datetime import date

from sqlmodel import Field, SQLModel


class Music(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    title: str
    author: int = Field(foreign_key="user.uidd")
    type: str | None = None
    duration: int | None = None
    file_path: str | None = None
    created_at: date = Field(default_factory=date.today)
