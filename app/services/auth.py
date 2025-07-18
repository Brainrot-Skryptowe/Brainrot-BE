from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta

import jwt
from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlmodel import Session, select

from app.core.config import settings
from app.db.models.user import User
from app.db.session import get_session

JWT_SECRET = settings.SECRET_KEY
JWT_ALGORITHM = "HS256"
JWT_EXPIRE_MINUTES = 60

security = HTTPBearer()


@dataclass
class AccessToken:
    token: str
    expires_at: datetime


def create_access_token(
    data: dict, expires_delta: timedelta | None = None
) -> AccessToken:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=JWT_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET, algorithm=JWT_ALGORITHM)
    return AccessToken(token=encoded_jwt, expires_at=expire)


def get_user_by_email(
    email: str, db: Session, is_error_detected=True, raise_exception=True
) -> User | None:
    user = db.exec(select(User).where(User.email == email)).first()
    if raise_exception and not user and is_error_detected:
        raise HTTPException(status_code=404, detail="User not found")
    return user


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_session),
) -> User:
    token = credentials.credentials
    credentials_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except Exception:
        raise credentials_exception
    user = get_user_by_email(email, db)
    if user is None:
        raise credentials_exception
    return user


def require_admin(current_user: User = Depends(get_current_user)):
    if getattr(current_user, "role", None) != "ADMIN":
        raise HTTPException(status_code=403, detail="Admin privileges required")
    return current_user
