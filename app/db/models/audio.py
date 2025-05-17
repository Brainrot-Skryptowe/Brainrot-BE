from datetime import date
from typing import Optional

from sqlmodel import Field, SQLModel


class Audio(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    text: str
    voice: int
    language: str
    speed: float
    file_path: Optional[str] = None
    created_at: date = Field(default_factory=date.today)
