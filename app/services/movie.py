import os
from typing import List, Optional

from fastapi import UploadFile
from sqlmodel import Session, select

from app.core.storage import SupabaseStorageBackend
from app.db.models.movie import Movie


def get_movie(db: Session, movie_id: int) -> Optional[Movie]:
    return db.get(Movie, movie_id)


def get_movies(db: Session, skip: int = 0, limit: int = 100) -> List[Movie]:
    return db.exec(select(Movie).offset(skip).limit(limit)).all()


def create_movie(
    db: Session, storage: SupabaseStorageBackend, movie_file: UploadFile
) -> Movie:
    filename = os.path.splitext(movie_file.filename)[0]
    extension = os.path.splitext(movie_file.filename)[1]

    db_movie = Movie(
        title=filename,
        type=extension.lstrip("."),
    )
    db.add(db_movie)
    db.commit()
    db.refresh(db_movie)

    storage_filename = f"{db_movie.id}{extension}"
    movie_file.file.seek(0)

    file_bytes = movie_file.file.read()
    file_dest = storage.upload_file(file_bytes, storage_filename)

    db_movie.file_path = file_dest
    db.commit()
    db.refresh(db_movie)

    return db_movie


def delete_movie(
    db: Session, storage: SupabaseStorageBackend, movie_id: int
) -> bool:
    db_movie = db.get(Movie, movie_id)
    if not db_movie:
        return False
    if db_movie.file_path:
        storage.delete_file(f"{db_movie.id}.{db_movie.type}")
    db.delete(db_movie)
    db.commit()
    return True
