from datetime import date

from pydantic import BaseModel

from app.db.models.srt import Srt


class SrtBase(BaseModel):
    id: int
    audio_id: int
    created_at: date
    file_path: str

    @classmethod
    def from_orm(cls, srt: Srt) -> "SrtBase":
        return cls(
            id=srt.id,
            created_at=srt.created_at,
            file_path=srt.file_path,
            audio_id=srt.audio_id,
        )
