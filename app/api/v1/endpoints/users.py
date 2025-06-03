from fastapi import APIRouter, Depends
from sqlmodel import Session, select

import app.services.auth as auth_services
import app.services.user as user_services
from app.core.storage.backends import (
    SupabaseStorageBackend,
    get_supabase_storage,
)
from app.db.models.user import User
from app.db.session import get_session
from app.schemas.user import (
    Token,
    UserChangePassword,
    UserGoogleAuth,
    UserLogIn,
    UserRead,
    UserReadByAdmin,
    UserRegister,
    UserUpdateDetailsByAdmin,
    UserUpdateSocials,
)

router = APIRouter()


# Guest endpoints
@router.post("/register", response_model=Token, status_code=201)
def register_user(
    user_data: UserRegister,
    db: Session = Depends(get_session),
    storage: SupabaseStorageBackend = Depends(get_supabase_storage),
):
    return user_services.register_user(user_data, db, storage)


@router.post("/login", response_model=Token)
def login_user(user_data: UserLogIn, db: Session = Depends(get_session)):
    return user_services.login_user(user_data, db)


@router.post("/google/auth", response_model=Token)
def google_auth(body: UserGoogleAuth, db: Session = Depends(get_session)):
    return user_services.google_auth(body, db)


# Admin-only endpoints
@router.get("/", response_model=list[UserReadByAdmin])
def get_users(
    db: Session = Depends(get_session),
    _: User = Depends(auth_services.require_admin),
):
    return db.exec(select(User))


@router.get("/email", response_model=UserReadByAdmin)
def get_user_by_email(
    email: str,
    db: Session = Depends(get_session),
    _: User = Depends(auth_services.require_admin),
):
    return auth_services.get_user_by_email(email, db)


@router.get("/id/{uidd}", response_model=UserReadByAdmin)
def get_user_by_uidd(
    uidd: int,
    db: Session = Depends(get_session),
    _: User = Depends(auth_services.require_admin),
):
    return user_services.get_user_by_uidd(uidd, db)


@router.patch("/id/{uidd}", response_model=UserReadByAdmin)
def update_user_by_uidd(
    uidd: int,
    user_data: UserUpdateDetailsByAdmin,
    db: Session = Depends(get_session),
    _: User = Depends(auth_services.require_admin),
):
    return user_services.update_user_details_by_admin(uidd, user_data, db)


@router.delete("/id/{uidd}", status_code=204)
def delete_user_by_uidd(
    uidd: int,
    db: Session = Depends(get_session),
    _: User = Depends(auth_services.require_admin),
):
    user_services.delete_user(uidd, db)


# User-only endpoints
@router.get("/me", response_model=UserRead)
def get_me(current_user: User = Depends(auth_services.get_current_user)):
    return current_user


@router.patch("/password", response_model=UserRead)
def change_user_password(
    user_data: UserChangePassword,
    db: Session = Depends(get_session),
    current_user: User = Depends(auth_services.get_current_user),
):
    return user_services.change_user_password(current_user.uidd, user_data, db)


@router.patch("/socials", response_model=UserRead)
def update_user_socials(
    user_data: UserUpdateSocials,
    db: Session = Depends(get_session),
    current_user: User = Depends(auth_services.get_current_user),
):
    return user_services.update_user_socials(current_user.uidd, user_data, db)


@router.delete("/me", status_code=204)
def delete_me(
    db: Session = Depends(get_session),
    current_user: User = Depends(auth_services.get_current_user),
):
    user_services.delete_user(current_user.uidd, db)
