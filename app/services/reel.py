import os

from sqlmodel import Session, select

from app.core.reel_generator import ReelGenerator
from app.core.storage.backends import SupabaseStorageBackend
from app.db.models.audio import Audio
from app.db.models.reel import Reel
from app.schemas.audio import AudioRead
from app.schemas.reel import ReelCreate, ReelWithAudio


def get_reel(db: Session, reel_id: int) -> ReelWithAudio | None:
    reel = db.get(Reel, reel_id)
    if not reel:
        return None
    audio = db.get(Audio, reel.audio_id) if reel.audio_id else None
    audio_read = AudioRead.from_orm(audio) if audio else None
    return ReelWithAudio(
        id=reel.id,
        lang=reel.lang,
        file_path=reel.file_path,
        movie_id=reel.movie_id,
        author=reel.author,
        audio=audio_read,
    )


def get_reels(
    db: Session, skip: int = 0, limit: int = 100
) -> list[ReelWithAudio]:
    reels = db.exec(select(Reel).offset(skip).limit(limit)).all()
    result = []
    for reel in reels:
        audio = db.get(Audio, reel.audio_id) if reel.audio_id else None
        audio_read = AudioRead.from_orm(audio) if audio else None
        result.append(
            ReelWithAudio(
                id=reel.id,
                lang=reel.lang,
                file_path=reel.file_path,
                movie_id=reel.movie_id,
                author=reel.author,
                audio=audio_read,
            )
        )
    return result


def get_reel_by_user(
    db: Session, user_id: int, reel_id: int
) -> ReelWithAudio | None:
    reel = db.exec(
        select(Reel).where(Reel.author == user_id, Reel.id == reel_id)
    ).first()
    if not reel:
        return None
    audio = db.get(Audio, reel.audio_id) if reel.audio_id else None
    audio_read = AudioRead.from_orm(audio) if audio else None
    return ReelWithAudio(
        id=reel.id,
        lang=reel.lang,
        file_path=reel.file_path,
        movie_id=reel.movie_id,
        author=reel.author,
        audio=audio_read,
    )


def get_reels_by_user(
    db: Session, user_id: int, skip: int = 0, limit: int = 100
) -> list[ReelWithAudio]:
    reels = db.exec(
        select(Reel).where(Reel.author == user_id).offset(skip).limit(limit)
    ).all()
    result = []
    for reel in reels:
        audio = db.get(Audio, reel.audio_id) if reel.audio_id else None
        audio_read = AudioRead.from_orm(audio) if audio else None
        result.append(
            ReelWithAudio(
                id=reel.id,
                lang=reel.lang,
                file_path=reel.file_path,
                movie_id=reel.movie_id,
                author=reel.author,
                audio=audio_read,
            )
        )
    return result


def create_reel(
    db: Session,
    storage: SupabaseStorageBackend,
    reel_info: ReelCreate,
    movie: bytes,
    audio: bytes | None,
    music: bytes | None,
    music_volume: float | None,
    srt: bytes | None,
    lang: str,
    user_id: int,
) -> Reel:
    reel_path = _generate_reel(movie, audio, srt, music, music_volume)

    db_reel = Reel(
        lang=lang,
        author=user_id,
        movie_id=reel_info.movie_id,
        audio_id=reel_info.audio_id,
    )
    db.add(db_reel)
    db.commit()
    db.refresh(db_reel)

    storage_filename = f"reel_{db_reel.id}.mp4"
    with open(reel_path, "rb") as reel_file:
        reel_file.seek(0)

        file_bytes = reel_file.read()
        file_dest = storage.upload_file(file_bytes, storage_filename)

    db_reel.file_path = file_dest
    db.commit()
    db.refresh(db_reel)
    reel_file.close()
    os.remove(reel_path)

    return db_reel


def delete_reel(
    db: Session, storage: SupabaseStorageBackend, reel_id: int
) -> bool:
    db_reel = db.get(Reel, reel_id)
    if not db_reel:
        return False
    if db_reel.file_path:
        storage.delete_file(f"reel_{db_reel.id}.mp4")
    db.delete(db_reel)
    db.commit()
    return True


def _generate_reel(
    movie: bytes,
    audio: bytes | None = None,
    srt: bytes | None = None,
    music: bytes | None = None,
    music_volume: float = 0.2,
    font: str = "Lato-Regular.ttf",
) -> str:
    generator = ReelGenerator(
        font_filename=font,
    )

    output_path = generator.generate(
        movie_bytes=movie,
        audio_bytes=audio,
        srt_bytes=srt,
        music_bytes=music,
        music_volume=music_volume,
    )
    return output_path
