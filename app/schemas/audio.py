from datetime import date

from pydantic import BaseModel

from app.db.models.audio import Audio
from app.models.shared.language import Language
from app.models.transcription.transcription_model import TranscriptionModel
from app.models.tts.voice import Voice
from app.schemas.srt import SrtBase  # Add this import


class AudioBase(BaseModel):
    title: str
    text: str
    voice: Voice
    language: Language
    speed: float | None = None


class AudioRead(AudioBase):
    id: int
    created_at: date
    file_path: str
    srtObject: SrtBase | None = None  # Add this field

    class Config:
        orm_mode = True

    @classmethod
    def from_orm(cls, audio: Audio) -> "AudioRead":
        # ...existing code...
        srt_obj = None
        if hasattr(audio, "srt") and audio.srt:
            srt_obj = SrtBase.from_orm(audio.srt)
        return cls(
            id=audio.id,
            title=audio.title,
            text=audio.text,
            voice=Voice.from_id(audio.voice),
            language=Language(audio.language),
            speed=audio.speed,
            created_at=audio.created_at,
            file_path=audio.file_path,
            srtObject=srt_obj,
        )


class AudioCreate(AudioBase):
    pass


class AudioTranscriptionCreate(BaseModel):
    audio_id: int
    transcription_model: TranscriptionModel
