from datetime import date

from sqlmodel import Field, SQLModel


class User(SQLModel, table=True):
    uidd: int | None = Field(default=None, primary_key=True)
    nick: str
    email: str
    password: str
    profile_image_url: str | None = None
    tiktok_link: str | None = None
    ig_link: str | None = None
    yt_link: str | None = None
    fb_link: str | None = None
    created_at: date = Field(default_factory=date.today)
    role: str = Field(default="USER")
