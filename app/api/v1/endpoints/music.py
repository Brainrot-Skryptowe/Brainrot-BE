from fastapi import APIRouter, Depends, File, Form, UploadFile
from sqlmodel import Session

import app.services.auth as auth_services
from app.core.storage.backends import (
    SupabaseStorageBackend,
    get_supabase_storage,
)
from app.db.models.music import Music
from app.db.models.user import User
from app.db.session import get_session
from app.schemas.music import MusicCreate, MusicRead
from app.services import music as services_music

router = APIRouter()


# Admin-only endpoints
@router.get("/admin/", response_model=list[MusicRead])
def read_all_music(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_session),
    _: User = Depends(auth_services.require_admin),
):
    return services_music.get_all_music(db, skip=skip, limit=limit)


@router.get("/{music_id}/admin", response_model=Music)
def read_music(
    music_id: int,
    db: Session = Depends(get_session),
    _: User = Depends(auth_services.require_admin),
):
    return services_music.get_music(db, music_id)


@router.delete("/{music_id}/admin", status_code=204)
def delete_music(
    music_id: int,
    db: Session = Depends(get_session),
    storage: SupabaseStorageBackend = Depends(get_supabase_storage),
    _: User = Depends(auth_services.require_admin),
):
    services_music.delete_music(db, storage, music_id)


# User-specific endpoints
@router.post("/", response_model=MusicRead, status_code=201)
def create_music(
    title: str = Form(...),
    music_file: UploadFile = File(...),
    db: Session = Depends(get_session),
    storage: SupabaseStorageBackend = Depends(get_supabase_storage),
    current_user: User = Depends(auth_services.get_current_user),
):
    music_info = MusicCreate(title=title)
    return services_music.create_music(
        db, current_user.uidd, storage, music_file, music_info
    )


@router.get("/", response_model=list[MusicRead])
def read_user_all_music(
    db: Session = Depends(get_session),
    current_user: User = Depends(auth_services.get_current_user),
    sort_by: str = "title",
    sort_dir: str = "asc",
):
    return services_music.get_all_music_by_user(
        db, current_user.uidd, sort_by, sort_dir
    )


@router.get("/{music_id}", response_model=MusicRead)
def read_user_music(
    music_id: int,
    db: Session = Depends(get_session),
    current_user: User = Depends(auth_services.get_current_user),
):
    return services_music.get_user_music(db, current_user.uidd, music_id)


@router.delete("/{music_id}", status_code=204)
def delete_user_music(
    music_id: int,
    db: Session = Depends(get_session),
    storage: SupabaseStorageBackend = Depends(get_supabase_storage),
    current_user: User = Depends(auth_services.get_current_user),
):
    services_music.delete_music_by_user(
        db, current_user.uidd, storage, music_id
    )
