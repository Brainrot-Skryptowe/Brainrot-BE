from datetime import date
from typing import TYPE_CHECKING, Optional

from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from app.db.models.reel import Reel
    from app.db.models.srt import Srt


class Audio(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    title: str
    text: str
    voice: int
    language: str
    speed: float
    file_path: str | None = None
    author: int = Field(foreign_key="user.uidd")
    created_at: date = Field(default_factory=date.today)
    reel: Optional["Reel"] = Relationship(back_populates="audio")
    srt: Optional["Srt"] = Relationship(
        back_populates="audio",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"},
    )
