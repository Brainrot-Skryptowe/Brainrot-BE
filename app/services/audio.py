import datetime
import io
from collections.abc import Sequence

import numpy as np
import soundfile as sf
from kokoro import KPipeline
from sqlmodel import Session, select

from app.core.storage.backends import SupabaseStorageBackend
from app.db.models.audio import Audio
from app.schemas.audio import AudioCreate, AudioRead

DEFAULT_SAMPLE_RATE = 22050
DEFAULT_FILE_FORMAT = "WAV"


def validate_audio(audio: Audio) -> bool:
    if audio.size == 0:
        raise ValueError("Generated audio is empty")


def get_audio(db: Session, audio_id: int) -> AudioRead | None:
    result = db.get(Audio, audio_id)
    if result is None:
        return None
    return AudioRead.from_orm(result)


def get_audios(
    db: Session, skip: int = 0, limit: int = 100
) -> Sequence[AudioRead]:
    results = db.exec(select(Audio).offset(skip).limit(limit)).all()
    return [AudioRead.from_orm(obj) for obj in results]


def create_audio(
    db: Session, storage: SupabaseStorageBackend, audio_create: AudioCreate
) -> AudioRead:
    audio = _generate_audio(audio_create)
    validate_audio(audio)

    timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    filename = (
        f"{audio_create.text[:10]}_{audio_create.voice.value}"
        f"_{audio_create.language.value}_{timestamp}.wav"
    )
    file_dest = _upload_audio(filename, audio, storage)

    db_audio = Audio(
        title=filename,
        text=audio_create.text,
        voice=audio_create.voice.id,
        language=audio_create.language.value,
        speed=audio_create.speed or 1.0,
        file_path=file_dest,
    )
    db.add(db_audio)
    db.commit()
    db.refresh(db_audio)
    return AudioRead.from_orm(db_audio)


def delete_audio(
    db: Session, storage: SupabaseStorageBackend, audio_id: int
) -> bool:
    db_audio = db.get(Audio, audio_id)
    if not db_audio:
        return False
    if db_audio.file_path:
        storage.delete_file(f"{db_audio.file_path}")
    db.delete(db_audio)
    db.commit()
    return True


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
