from fastapi import HTTPException
from passlib.context import CryptContext
from sqlmodel import Session, select

from app.db.models.user import User
from app.schemas.user import *

# singleton
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def create_user(db: Session, user_data: UserCreate) -> User:
    if get_user_by_email(db, user_data.email):
        raise HTTPException(status_code=400, detail="Account with provided email already exists")
    
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


def get_user_by_email(db: Session, email: str) -> User:
    return db.exec(select(User).where(User.email == email)).first()


def update_user_socials(db: Session, uidd: int, new_data: UserUpdateSocials) -> User:
    user = db.get(User, uidd)
    
    for attr_name, attr_value in user.model_dump(exclude_unset=True).items():
        setattr(user, attr_name, attr_value)
    
    db.commit()
    db.refresh(user)
    return user

def update_user_password(db: Session, uidd: int, new_data: UserUpdatePassword) -> User:
    user = db.get(User, uidd)
    
    if not PasswordHasher.verify_password(new_data.old_password, user.password):
        raise HTTPException(status_code=401, detail="Invalid old password")
    
    user.password = PasswordHasher.hash_password(new_data.new_password)
    
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
    