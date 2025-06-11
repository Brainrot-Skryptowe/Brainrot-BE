from pydantic import BaseModel

from app.models.shared.language import Language


class ReelTextRequest(BaseModel):
    description: str
    duration: int
    target_lang: Language = Language.English


class ReelTextResponse(BaseModel):
    text: str
