import io
from datetime import date

import httpx
from fastapi import HTTPException
from passlib.context import CryptContext
from PIL import Image, ImageDraw, ImageFont
from sqlmodel import Session

from app.core.storage.backends import SupabaseStorageBackend
from app.db.models.user import User
from app.schemas.user import (
    Token,
    UserChangePassword,
    UserGoogleAuth,
    UserLogIn,
    UserRegister,
    UserUpdateSocials,
)
from app.services.auth import create_access_token, get_user_by_email

# singleton
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def register_user(
    user_data: UserRegister, db: Session, storage: SupabaseStorageBackend
) -> Token:
    if get_user_by_email(user_data.email, db, is_error_detected=False):
        raise HTTPException(
            status_code=400, detail="Account with provided email already exists"
        )

    hashed_password = PasswordHasher.hash_password(user_data.password)

    profile_picture_url = _create_and_upload_avatar(user_data.nick, storage)

    user = User(
        email=user_data.email,
        nick=user_data.nick,
        password=hashed_password,
        tiktok_link=user_data.tiktok_link,
        profile_image_url=profile_picture_url,
        ig_link=user_data.ig_link,
        yt_link=user_data.yt_link,
        fb_link=user_data.fb_link,
    )

    db.add(user)
    db.commit()
    db.refresh(user)
    token_data = create_access_token({"sub": user.email, "uidd": user.uidd})
    return Token(
        access_token=token_data.token,
        token_type="bearer",
        expires_at=token_data.expires_at,
    )


def refresh_token(current_user: User) -> Token:
    token_data = create_access_token(
        {"sub": current_user.email, "uidd": current_user.uidd}
    )
    return Token(
        access_token=token_data.token,
        token_type="bearer",
        expires_at=token_data.expires_at,
    )


def login_user(user_data: UserLogIn, db: Session) -> Token:
    user = get_user_by_email(user_data.email, db)

    error_msg = "Invalid email or password"

    if not user:
        print("notuser")
        raise HTTPException(status_code=404, detail=error_msg)

    if not PasswordHasher.verify_password(user_data.password, user.password):
        raise HTTPException(status_code=401, detail=error_msg)
    token_data = create_access_token({"sub": user.email, "uidd": user.uidd})
    return Token(
        access_token=token_data.token,
        token_type="bearer",
        expires_at=token_data.expires_at,
    )


def google_auth(body: UserGoogleAuth, db: Session) -> Token:
    headers = {"Authorization": f"Bearer {body.access_token}"}
    resp = httpx.get(
        "https://www.googleapis.com/oauth2/v3/userinfo", headers=headers
    )

    if resp.status_code != 200:
        raise HTTPException(
            status_code=401, detail="Invalid Google access token"
        )

    user_info = resp.json()

    user = get_user_by_email(user_info["email"], db, raise_exception=False)
    if not user:
        email = user_info["email"]
        user = User(
            email=email,
            nick=email.split("@")[0],
            password="",
            profile_image_url=user_info["picture"],
            created_at=date.today(),
        )
        db.add(user)
        db.commit()
        db.refresh(user)

    token_data = create_access_token({"sub": user.email, "uidd": user.uidd})
    return Token(
        access_token=token_data.token,
        token_type="bearer",
        expires_at=token_data.expires_at,
    )


def get_user_by_uidd(uidd: int, db: Session, is_error_detected=True) -> User:
    user = db.get(User, uidd)
    if not user and is_error_detected:
        raise HTTPException(status_code=404, detail="User not found")
    return user


def update_user_details_by_admin(
    uidd: int, user_data: UserUpdateSocials, db: Session
) -> User:
    user = get_user_by_uidd(uidd, db)
    if user_data.password:
        user_data.password = PasswordHasher.hash_password(user_data.password)
    for attr, value in user_data.model_dump(exclude_unset=True).items():
        if attr != "password":
            setattr(user, attr, value)

    db.commit()
    db.refresh(user)
    return user


def update_user_socials(
    uidd: int, user_data: UserUpdateSocials, db: Session
) -> User:
    user = get_user_by_uidd(uidd, db)

    for attr, value in user_data.model_dump(exclude_unset=True).items():
        setattr(user, attr, value)

    db.commit()
    db.refresh(user)
    return user


def delete_user(uidd: int, db: Session) -> None:
    user = get_user_by_uidd(uidd, db)
    db.delete(user)
    db.commit()


def change_user_password(
    uidd: int, user_data: UserChangePassword, db: Session
) -> User:
    user = get_user_by_uidd(uidd, db)

    if not PasswordHasher.verify_password(
        user_data.old_password, user.password
    ):
        raise HTTPException(status_code=401, detail="Invalid old password")

    user.password = PasswordHasher.hash_password(user_data.new_password)

    db.commit()
    db.refresh(user)
    return user


def _create_and_upload_avatar(
    nick: str, storage: SupabaseStorageBackend
) -> str:
    size = (256, 256)
    bg_color = (30, 144, 255)
    text_color = (255, 255, 255)
    font_size = 1200

    img = Image.new("RGB", size, bg_color)
    draw = ImageDraw.Draw(img)

    try:
        font = ImageFont.truetype("arial.ttf", font_size)
    except Exception:
        font = ImageFont.load_default()

    letter = nick[0].upper() if nick else "?"
    # Use textbbox for Pillow >=10
    bbox = draw.textbbox((0, 0), letter, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    position = ((size[0] - text_width) // 2, (size[1] - text_height) // 2)

    draw.text(position, letter, fill=text_color, font=font)

    buf = io.BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)

    filename = f"user_avatar_{nick}.png"
    file_url = storage.upload_file(buf.read(), filename)
    return file_url


class PasswordHasher:
    @staticmethod
    def hash_password(password: str) -> str:
        return pwd_context.hash(password)

    @staticmethod
    def verify_password(input_password: str, hashed_password: str) -> bool:
        return pwd_context.verify(input_password, hashed_password)
