from pydantic import BaseModel


class UserBase(BaseModel):
    email: str
    tiktok_link: str | None = None
    ig_link: str | None = None
    yt_link: str | None = None
    fb_link: str | None = None


class UserRead(UserBase):
    uidd: int

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


class UserUpdatePassword(BaseModel):
    old_password: str
    new_password: str

    class Config:
        orm_mode = True
