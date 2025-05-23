from datetime import date

from pydantic import BaseModel

from app.db.models.audio import Audio
from app.models.shared.language import Language
from app.models.tts.voice import Voice


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

    class Config:
        orm_mode = True

    @classmethod
    def from_orm(cls, audio: Audio) -> "AudioRead":
        return cls(
            id=audio.id,
            title=audio.title,
            text=audio.text,
            voice=Voice.from_id(audio.voice),
            language=Language(audio.language),
            speed=audio.speed,
            created_at=audio.created_at,
            file_path=audio.file_path,
        )


class AudioCreate(AudioBase):
    pass
