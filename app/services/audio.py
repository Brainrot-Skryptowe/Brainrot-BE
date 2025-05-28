import datetime
import io
from collections.abc import Sequence
from datetime import date

import numpy as np
import soundfile as sf
from kokoro import KPipeline
from sqlmodel import Session, select

from app.core.storage.backends import SupabaseStorageBackend
from app.core.transcription import Transcriber
from app.db.models.audio import Audio
from app.db.models.srt import Srt
from app.models.transcription.transcription import Transcription
from app.models.transcription.transcription_model import TranscriptionModel
from app.schemas.audio import AudioCreate, AudioRead
from app.schemas.srt import SrtBase
from app.utils import srt

DEFAULT_SAMPLE_RATE = 22050
DEFAULT_FILE_FORMAT = "WAV"


def validate_audio(audio: Audio) -> bool:
    if audio.size == 0:
        raise ValueError("Generated audio is empty")


def get_audio(db: Session, audio_id: int) -> AudioRead | None:
    audio = db.get(Audio, audio_id)
    if audio is None:
        return None
    stmt = select(Srt).where(Srt.audio_id == audio_id)
    srt_obj = db.exec(stmt).first()
    audio.srt = srt_obj
    return AudioRead.from_orm(audio)


def get_audios(
    db: Session, skip: int = 0, limit: int = 100
) -> Sequence[AudioRead]:
    results = db.exec(select(Audio).offset(skip).limit(limit)).all()
    audio_reads = []
    for audio in results:
        stmt = select(Srt).where(Srt.audio_id == audio.id)
        srt_obj = db.exec(stmt).first()
        audio.srt = srt_obj
        audio_reads.append(AudioRead.from_orm(audio))
    return audio_reads


def get_audios_by_user(
    db: Session, user_id: int, skip: int = 0, limit: int = 100
) -> Sequence[AudioRead]:
    stmt = (
        select(Audio).where(Audio.author == user_id).offset(skip).limit(limit)
    )
    results = db.exec(stmt).all()
    audio_reads = []
    for audio in results:
        stmt = select(Srt).where(Srt.audio_id == audio.id)
        srt_obj = db.exec(stmt).first()
        audio.srt = srt_obj
        audio_reads.append(AudioRead.from_orm(audio))
    return audio_reads


def get_audio_by_user(
    db: Session, user_id: int, audio_id: int
) -> AudioRead | None:
    stmt = select(Audio).where(Audio.author == user_id, Audio.id == audio_id)
    audio = db.exec(stmt).first()
    if audio is None:
        return None
    stmt = select(Srt).where(Srt.audio_id == audio_id)
    srt_obj = db.exec(stmt).first()
    audio.srt = srt_obj
    return AudioRead.from_orm(audio)


def create_audio(
    db: Session,
    storage: SupabaseStorageBackend,
    audio_create: AudioCreate,
    user_id: int,
) -> AudioRead:
    audio = _generate_audio(audio_create)
    validate_audio(audio)

    timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    title = (
        f"{audio_create.text[:10]}_{audio_create.voice.value}"
        f"_{audio_create.language.value}_{timestamp}.wav"
    )

    db_audio = Audio(
        author=user_id,
        title=title,
        text=audio_create.text,
        voice=audio_create.voice.id,
        language=audio_create.language.value,
        speed=audio_create.speed or 1.0,
    )
    db.add(db_audio)
    db.commit()
    db.refresh(db_audio)

    file_dest = _upload_audio(f"audio_{db_audio.id}.wav", audio, storage)

    db_audio.file_path = file_dest
    db.commit()
    db.refresh(db_audio)

    return AudioRead.from_orm(db_audio)


def delete_audio(
    db: Session, storage: SupabaseStorageBackend, audio_id: int
) -> bool:
    db_audio = db.get(Audio, audio_id)
    if not db_audio:
        return False
    stmt = select(Srt).where(Srt.audio_id == audio_id)
    db_srt = db.exec(stmt).first()
    if db_srt:
        db.delete(db_srt)
    if db_audio.file_path:
        storage.delete_file(f"{db_audio.file_path}")
    db.delete(db_audio)
    db.commit()
    return True


def delete_audio_by_user(
    db: Session, user_id: int, storage: SupabaseStorageBackend, audio_id: int
) -> bool:
    db_audio = get_audio_by_user(db, user_id, audio_id)
    if not db_audio:
        return False
    delete_audio(db, storage, db_audio.id)


def transcribe_audio_file(
    db: Session,
    storage: SupabaseStorageBackend,
    audio_id: int,
    audio_bytes: bytes,
    model: TranscriptionModel,
) -> SrtBase:
    transcription = Transcriber.transcribe(audio_bytes, model)
    file_dest = _upload_transcription(audio_id, transcription, storage)

    stmt = select(Srt).where(Srt.audio_id == audio_id)
    db_srt = db.exec(stmt).first()

    if db_srt:
        db_srt.file_path = file_dest
        db_srt.created_at = date.today()
    else:
        db_srt = Srt(
            audio_id=audio_id,
            file_path=file_dest,
        )
        db.add(db_srt)

    db.commit()
    db.refresh(db_srt)
    return SrtBase.from_orm(db_srt)


def _upload_transcription(
    audio_id: int, transcription: Transcription, storage: SupabaseStorageBackend
) -> str:
    buffer = io.BytesIO()
    srt_content = srt.generate_srt(transcription)
    buffer.write(srt_content.encode("utf-8"))
    buffer.seek(0)
    filename = f"transcription_{audio_id}.srt"
    file_dest = storage.upload_file(buffer.read(), filename, True)
    return file_dest


def _upload_audio(
    filename: str, audio: np.ndarray, storage: SupabaseStorageBackend
) -> str:
    validate_audio(audio)

    buffer = io.BytesIO()
    sf.write(
        buffer,
        audio,
        DEFAULT_SAMPLE_RATE,
        format=DEFAULT_FILE_FORMAT,
        subtype="PCM_16",
    )
    buffer.seek(0)
    file_dest = storage.upload_file(buffer.read(), filename)
    return file_dest


def _generate_audio(audio_create: AudioCreate) -> np.ndarray:
    pipeline = KPipeline(lang_code=audio_create.language.value)
    generator = pipeline(
        audio_create.text,
        voice=audio_create.voice.value,
        speed=audio_create.speed or 1.0,
        split_pattern=r"\n+",
    )

    audios: list[np.ndarray] = []
    for _, _, audio in generator:
        audios.append(audio)

    if not audios:
        return np.array([], dtype=np.float32)

    final_audio = np.concatenate(audios)
    return final_audio
