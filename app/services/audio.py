from typing import List, Optional, Sequence

import numpy as np
from kokoro import KPipeline
from sqlmodel import Session, select

from app.core.storage.backends import SupabaseStorageBackend
from app.db.models.audio import Audio
from app.db.models.movie import Movie
from app.schemas.audio import AudioCreate


def get_audio(db: Session, audio_id: int) -> Optional[Movie]:
    return db.get(Audio, audio_id)


def get_audios(db: Session, skip: int = 0, limit: int = 100) -> Sequence[Audio]:
    return db.exec(select(Audio).offset(skip).limit(limit)).all()


def create_audio(
    db: Session, storage: SupabaseStorageBackend, audio_create: AudioCreate
) -> Audio:
    audio = _generate_audio(audio_create)
    if audio.size == 0:
        raise ValueError("Generated audio is empty")

    filename = f"{audio_create.text[:10]}_{audio_create.voice.value}_{audio_create.language.value}.wav"

    file_dest = storage.upload_file(audio.data.tobytes(), filename)

    db_audio = Audio(
        title=filename,
        text=audio_create.text,
        voice=audio_create.voice.value,
        language=audio_create.language.value,
        speed=audio_create.speed or 1.0,
        file_path=file_dest,
    )
    db.add(db_audio)
    db.commit()
    db.refresh(db_audio)
    return db_audio


def _generate_audio(audio_create: AudioCreate) -> np.ndarray:
    pipeline = KPipeline(lang_code=audio_create.language.value)
    generator = pipeline(
        audio_create.text,
        voice=audio_create.voice.value,
        speed=audio_create.speed or 1.0,
        split_pattern=r'\n+'
    )

    audios: List[np.ndarray] = []
    for i, (_, _, audio) in enumerate(generator):
        audios.append(audio)

    if not audios:
        return np.array([], dtype=np.float32)

    final_audio = np.concatenate(audios)
    return final_audio