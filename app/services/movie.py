import os
import tempfile

import imageio.v3 as iio
from fastapi import HTTPException, UploadFile
from moviepy import VideoFileClip
from sqlmodel import Session, asc, desc, select

from app.core.config import settings
from app.core.storage.backends import SupabaseStorageBackend
from app.db.models.movie import Movie
from app.schemas.audio import AudioRead
from app.schemas.movie import MovieCreate, MovieRead, MovieReadBasic
from app.schemas.reel import ReelWithAudio


def _build_movie_read(db_movie):
    reels = db_movie.reels if hasattr(db_movie, "reels") else []
    reel_reads = []
    for r in reels:
        audio = None
        if hasattr(r, "audio") and r.audio:
            audio = AudioRead.from_orm(r.audio)
        reel_reads.append(
            ReelWithAudio(
                id=r.id,
                lang=r.lang,
                file_path=r.file_path,
                movie_id=r.movie_id,
                author=r.author,
                audio=audio,
            )
        )
    return MovieRead(
        id=db_movie.id,
        title=db_movie.title,
        description=db_movie.description,
        native_lang=db_movie.native_lang,
        created_at=db_movie.created_at,
        author=db_movie.author,
        type=db_movie.type,
        duration=db_movie.duration,
        file_path=db_movie.file_path,
        thumbnail_path=db_movie.thumbnail_path,
        reels=reel_reads,
    )


def get_movie(db: Session, movie_id: int) -> MovieRead | None:
    db_movie = db.get(Movie, movie_id)
    if db_movie is None:
        raise HTTPException(status_code=404, detail="Movie not found")
    return _build_movie_read(db_movie)


def get_movies(db: Session, skip: int = 0, limit: int = 100) -> list[MovieRead]:
    db_movies = db.exec(select(Movie).offset(skip).limit(limit)).all()
    return [_build_movie_read(db_movie) for db_movie in db_movies]


def get_movies_by_user_basic(db: Session, user_id: int) -> list[MovieReadBasic]:
    return db.exec(select(Movie).where(Movie.author == user_id)).all()


def get_movies_by_user(
    db: Session, user_id: int, sort_by: str = "title", sort_dir: str = "asc"
) -> list[MovieRead]:
    sort_options = {
        "title": Movie.title,
        "duration": Movie.duration,
        "created_at": Movie.created_at,
    }

    sort_field = sort_options.get(sort_by, Movie.title)
    sort_order = asc if sort_dir.lower() == "asc" else desc

    db_movies = db.exec(
        select(Movie)
        .where(Movie.author == user_id)
        .order_by(sort_order(sort_field))
    ).all()
    return [_build_movie_read(db_movie) for db_movie in db_movies]


def get_movie_by_user(
    db: Session, user_id: int, movie_id: int
) -> MovieRead | None:
    db_movie = db.exec(
        select(Movie).where(Movie.author == user_id, Movie.id == movie_id)
    ).first()
    if db_movie is None:
        raise HTTPException(status_code=404, detail="Movie not found")
    return _build_movie_read(db_movie)


def get_video_duration(file_bytes: bytes) -> int:
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as tmp:
        tmp.write(file_bytes)
        tmp_path = tmp.name

    try:
        with VideoFileClip(tmp_path) as clip:
            duration = int(clip.duration)
    except Exception:
        os.unlink(tmp_path)
        raise ValueError("Cannot open video file for processing.")
    os.unlink(tmp_path)
    return duration


def get_video_thumbnail(file_bytes: bytes) -> bytes | None:
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as tmp:
        tmp.write(file_bytes)
        tmp_path = tmp.name

    thumbnail_bytes = None
    try:
        with VideoFileClip(tmp_path) as clip:
            frame_time = 0
            if clip.duration > 0.5:
                frame_time = min(0.5, clip.duration - 0.01)
            frame = clip.get_frame(frame_time)
            thumbnail_bytes = iio.imwrite(
                "<bytes>", frame, plugin="pillow", format="png"
            )
    except Exception:
        os.unlink(tmp_path)
        raise ValueError("Cannot open video file for processing.")
    os.unlink(tmp_path)
    return thumbnail_bytes


def create_movie(
    db: Session,
    user_uidd: int,
    storage: SupabaseStorageBackend,
    movie_file: UploadFile,
    movie_info: MovieCreate,
) -> Movie:
    extension = os.path.splitext(movie_file.filename)[1]

    if extension.lower() not in settings.ALLOWED_VIDEO_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail="Invalid file type. Only video files are allowed.",
        )
    file_bytes = movie_file.file.read()

    duration = get_video_duration(file_bytes)
    thumbnail_bytes = get_video_thumbnail(file_bytes)

    db_movie = Movie(
        title=movie_info.title,
        description=movie_info.description,
        author=user_uidd,
        native_lang=movie_info.native_lang,
        type=extension.lstrip("."),
        duration=duration,
    )
    db.add(db_movie)
    db.commit()
    db.refresh(db_movie)

    storage_filename = f"{db_movie.id}{extension}"
    file_dest = storage.upload_file(file_bytes, storage_filename)
    db_movie.file_path = file_dest

    if thumbnail_bytes:
        thumbnail_filename = f"{db_movie.id}.png"
        thumbnail_dest = storage.upload_file(
            thumbnail_bytes, thumbnail_filename
        )
        db_movie.thumbnail_path = thumbnail_dest

    db.commit()
    db.refresh(db_movie)

    return db_movie


def delete_movie(
    db: Session, storage: SupabaseStorageBackend, movie_id: int
) -> None:
    db_movie = db.get(Movie, movie_id)
    if not db_movie:
        raise HTTPException(status_code=404, detail="Movie not found")
    if db_movie.file_path:
        storage.delete_file(f"{db_movie.id}.{db_movie.type}")
    db.delete(db_movie)
    db.commit()


def delete_movie_by_user(
    db: Session, user_id: int, storage: SupabaseStorageBackend, movie_id: int
) -> None:
    db_movie = get_movie_by_user(db, user_id, movie_id)
    if not db_movie:
        raise HTTPException(status_code=404, detail="Movie not found")
    delete_movie(db, storage, db_movie.id)
