from datetime import date
from typing import Optional
from sqlmodel import SQLModel, Field

class User(SQLModel, table=True):
    uidd: Optional[int] = Field(default=None, primary_key=True)
    email: str
    password: str
    tiktok_link: Optional[str] = None
    ig_link: Optional[str] = None
    yt_link: Optional[str] = None
    fb_link: Optional[str] = None
    created_at: date = Field(default_factory=date.today)