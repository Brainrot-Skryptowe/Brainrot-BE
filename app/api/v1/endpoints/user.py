from fastapi import APIRouter, Depends
from sqlmodel import Session

import app.services.user as user_services
from app.db.session import get_session
from app.schemas.user import *

router = APIRouter()

@router.post("/users/", response_model=UserRead, status_code=200)
def register_user(user_data: UserRegister, db: Session = Depends(get_session)):
    return user_services.register_user(user_data, db)
