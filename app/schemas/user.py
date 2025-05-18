from typing import Optional

from pydantic import BaseModel


class UserBase(BaseModel):
    email: str
    tiktok_link: Optional[str] = None
    ig_link: Optional[str] = None
    yt_link: Optional[str] = None
    fb_link: Optional[str] = None


class UserRead(UserBase):
    uidd: int

    class Config:
        orm_mode = True


class UserRegister(UserBase):
    password: str

    class Config:
        orm_mode = True


class UserUpdateSocials(BaseModel):
    tiktok_link: Optional[str] = None
    ig_link: Optional[str] = None
    yt_link: Optional[str] = None
    fb_link: Optional[str] = None

    class Config:
        orm_mode = True


class UserUpdatePassword(BaseModel):
    old_password: str
    new_password: str

    class Config:
        orm_mode = True
