from datetime import date
from typing import Optional

from pydantic import BaseModel

from app.models.shared.language import Language
from app.models.tts.voice import Voice


class AudioBase(BaseModel):
    title: str
    text: str
    voice: Voice
    language: Language
    speed: Optional[float] = None


class AudioRead(AudioBase):
    id: int
    created_at: date

    class Config:
        orm_mode = True


class AudioCreate(AudioBase):
    pass
