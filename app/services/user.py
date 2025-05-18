from passlib.context import CryptContext
from sqlmodel import Session

from app.db.models.user import User
from app.schemas.user import *

# singleton
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def create_user(db: Session, user_data: UserCreate) -> User:
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



class PasswordHasher:
    
    @staticmethod
    def hash_password(password: str) -> str:
        return pwd_context.hash(password)
         
    @staticmethod
    def verify_password(input_password: str, hashed_password: str) -> bool:
        return pwd_context.verify(input_password, hashed_password)
    