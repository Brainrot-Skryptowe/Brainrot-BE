import datetime

from pydantic import BaseModel


class UserBase(BaseModel):
    email: str
    tiktok_link: str | None = None
    ig_link: str | None = None
    yt_link: str | None = None
    fb_link: str | None = None


class UserRead(UserBase):
    role: str
    created_at: datetime.date

    class Config:
        orm_mode = True


class UserReadByAdmin(UserBase):
    uidd: int
    created_at: datetime.date
    role: str

    class Config:
        orm_mode = True


class UserRegister(UserBase):
    password: str

    class Config:
        orm_mode = True


class UserLogIn(BaseModel):
    email: str
    password: str

    class Config:
        orm_mode = True


class UserUpdateSocials(BaseModel):
    tiktok_link: str | None = None
    ig_link: str | None = None
    yt_link: str | None = None
    fb_link: str | None = None

    class Config:
        orm_mode = True


class UserUpdateDetailsByAdmin(BaseModel):
    tiktok_link: str | None = None
    ig_link: str | None = None
    yt_link: str | None = None
    fb_link: str | None = None
    role: str | None = None
    password: str | None = None

    class Config:
        orm_mode = True


class UserChangePassword(BaseModel):
    old_password: str
    new_password: str

    class Config:
        orm_mode = True


class Token(BaseModel):
    access_token: str
    token_type: str
