from fastapi import HTTPException
from passlib.context import CryptContext
from sqlmodel import Session, select

from app.db.models.user import User
from app.schemas.user import (
    UserChangePassword,
    UserLogIn,
    UserRegister,
    UserUpdateSocials,
)

# singleton
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def register_user(user_data: UserRegister, db: Session) -> User:
    if get_user_by_email(user_data.email, db):
        raise HTTPException(
            status_code=400, detail="Account with provided email already exists"
        )

    hashed_password = PasswordHasher.hash_password(user_data.password)

    user = User(
        email=user_data.email,
        password=hashed_password,
        tiktok_link=user_data.tiktok_link,
        ig_link=user_data.ig_link,
        yt_link=user_data.yt_link,
        fb_link=user_data.fb_link,
    )

    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def login_user(user_data: UserLogIn, db: Session) -> User:
    user = get_user_by_email(user_data.email, db)

    error_msg = "Invalid email or password"

    if not user:
        print("notuser")
        raise HTTPException(status_code=404, detail=error_msg)

    if not PasswordHasher.verify_password(user_data.password, user.password):
        raise HTTPException(status_code=401, detail=error_msg)

    return user


def get_user_by_email(email: str, db: Session) -> User | None:
    return db.exec(select(User).where(User.email == email)).first()


def get_user_by_uidd(uidd: int, db: Session) -> User:
    user = db.get(User, uidd)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


def update_user_socials(user_data: UserUpdateSocials, db: Session) -> User:
    user = get_user_by_uidd(user_data.uidd, db)

    for attr, value in user_data.model_dump(exclude_unset=True).items():
        setattr(user, attr, value)

    db.commit()
    db.refresh(user)
    return user


def change_user_password(user_data: UserChangePassword, db: Session) -> User:
    user = get_user_by_uidd(user_data.uidd, db)

    if not PasswordHasher.verify_password(
        user_data.old_password, user.password
    ):
        raise HTTPException(status_code=401, detail="Invalid old password")

    user.password = PasswordHasher.hash_password(user_data.new_password)

    db.commit()
    db.refresh(user)
    return user


class PasswordHasher:
    @staticmethod
    def hash_password(password: str) -> str:
        return pwd_context.hash(password)

    @staticmethod
    def verify_password(input_password: str, hashed_password: str) -> bool:
        return pwd_context.verify(input_password, hashed_password)
