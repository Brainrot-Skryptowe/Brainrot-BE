from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

import app.services.user as user_services
from app.db.models.user import User
from app.db.session import get_session
from app.schemas.user import (
    UserChangePassword,
    UserLogIn,
    UserRead,
    UserRegister,
    UserUpdateSocials,
)

router = APIRouter()


@router.post("/register", response_model=UserRead, status_code=200)
def register_user(user_data: UserRegister, db: Session = Depends(get_session)):
    return user_services.register_user(user_data, db)


@router.post("/login", response_model=UserRead)
def login_user(user_data: UserLogIn, db: Session = Depends(get_session)):
    return user_services.login_user(user_data, db)


@router.post("google_auth", response_model=UserRead)
def google_auth(token: str, db: Session = Depends(get_session)):
    return user_services.google_auth(token, db)


@router.get("/", response_model=list[UserRead])
def get_users(db: Session = Depends(get_session)):
    return db.exec(select(User))


@router.get("/uidd/{uidd}", response_model=UserRead)
def get_user_by_uidd(uidd: str, db: Session = Depends(get_session)):
    return user_services.get_user_by_uidd(uidd, db)


@router.get("/email/{email}", response_model=UserRead)
def get_user_by_email(email: str, db: Session = Depends(get_session)):
    user = user_services.get_user_by_email(email, db)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.patch("/password", response_model=UserRead)
def change_user_password(
    user_data: UserChangePassword, db: Session = Depends(get_session)
):
    return user_services.change_user_password(user_data, db)


@router.patch("/socials", response_model=UserRead)
def update_user_socials(
    user_data: UserUpdateSocials, db: Session = Depends(get_session)
):
    return user_services.update_user_socials(user_data, db)


@router.delete("/{uidd}", status_code=204)
def delete_user(uidd: int, db: Session = Depends(get_session)):
    user_services.delete_user(uidd, db)
