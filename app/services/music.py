import os
from typing import Sequence

from fastapi import HTTPException, UploadFile
from sqlmodel import Session, asc, desc, select

from app.core.config import settings
from app.core.storage.backends import SupabaseStorageBackend
from app.db.models.music import Music
from app.schemas.music import MusicRead, MusicCreate
from app.services.utils import get_file_duration


def _music_to_read(db_music: Music) -> MusicRead:
    return MusicRead(
        id=db_music.id,
        title=db_music.title,
        author=db_music.author,
        type=db_music.type,
        duration=db_music.duration,
        created_at=db_music.created_at,
        file_path=db_music.file_path,
    )

def get_music(db: Session, music_id: int) -> Music | None:
    db_music = db.get(Music, music_id)
    if db_music is None:
        raise HTTPException(status_code=404, detail="Music not found")
    return db_music

def get_user_music(db: Session, user_id: int, music_id: int) -> MusicRead | None:
    db_music = db.exec(
        select(Music).where(Music.author == user_id, Music.id == music_id)
    ).first()
    if db_music is None:
        raise HTTPException(status_code=404, detail="Music not found")
    return _music_to_read(db_music)


def get_all_music(db: Session, skip: int = 0, limit: int = 100) -> Sequence[MusicRead]:
    db_all_music = db.exec(select(Music).offset(skip).limit(limit)).all()
    return [_music_to_read(db_music) for db_music in db_all_music]


def get_all_music_by_user(
    db: Session, user_id: int, sort_by: str = "title", sort_dir: str = "asc"
) -> Sequence[MusicRead]:
    sort_options = {
        "title": Music.title,
        "duration": Music.duration,
        "created_at": Music.created_at,
    }

    sort_field = sort_options.get(sort_by, Music.title)
    sort_order = asc if sort_dir.lower() == "asc" else desc

    db_all_music = db.exec(
        select(Music)
        .where(Music.author == user_id)
        .order_by(sort_order(sort_field))
    ).all()
    return [_music_to_read(db_music) for db_music in db_all_music]


def create_music(
    db: Session,
    user_uidd: int,
    storage: SupabaseStorageBackend,
    music_file: UploadFile,
    music_info: MusicCreate,
) -> MusicRead:
    extension = os.path.splitext(music_file.filename)[1]

    if extension.lower() not in settings.ALLOWED_MUSIC_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail= "Invalid file type. Only the following extensions are allowed: "
            + ", ".join(settings.ALLOWED_MUSIC_EXTENSIONS)
        )
    file_bytes = music_file.file.read()

    duration = get_file_duration(file_bytes, ".wav")

    db_music = Music(
        title=music_info.title,
        author=user_uidd,
        type=extension.lstrip("."),
        duration=duration,
    )
    db.add(db_music)
    db.commit()
    db.refresh(db_music)

    storage_filename = f"music_{db_music.id}{extension}"
    file_dest = storage.upload_file(file_bytes, storage_filename)
    db_music.file_path = file_dest


    db.commit()
    db.refresh(db_music)

    return _music_to_read(db_music)


def delete_music(
    db: Session, storage: SupabaseStorageBackend, music_id: int
) -> None:
    db_music = db.get(Music, music_id)
    if not db_music:
        raise HTTPException(status_code=404, detail="Music not found")
    _delete_music_file(db, storage, db_music)


def delete_music_by_user(
    db: Session, user_id: int, storage: SupabaseStorageBackend, mousic_id: int
) -> None:
    db_music = get_music(db, mousic_id)
    if not db_music or db_music.author != user_id:
        raise HTTPException(status_code=404, detail="Music not found")

    _delete_music_file(db, storage, db_music)

def _delete_music_file(
    db: Session, storage: SupabaseStorageBackend, db_music: Music) -> None:
    if db_music.file_path:
        storage.delete_file(f"music_{db_music.id}.{db_music.type}")

    db.delete(db_music)
    db.commit()
