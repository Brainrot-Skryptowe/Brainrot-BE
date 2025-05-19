from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from app.db.models.user import User
import app.services.user as user_services
from app.db.session import get_session
from app.schemas.user import *

router = APIRouter()


@router.post("/", response_model=UserRead, status_code=200)
def register_user(user_data: UserRegister, db: Session = Depends(get_session)):
    return user_services.register_user(user_data, db)

@router.get("/", response_model=list[UserRead])
def get_users(db: Session = Depends(get_session)):
    return db.exec(select(User))

@router.get("/uidd/{uidd}", response_model=UserRead)
def get_user_by_uidd(uidd: str, db: Session = Depends(get_session)):
    user = db.exec(select(User).where(User.uidd == uidd)).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.get("/email/{email}", response_model=UserRead)
def get_user_by_email(email: str, db: Session = Depends(get_session)):
    user = user_services.get_user_by_email(email, db)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

