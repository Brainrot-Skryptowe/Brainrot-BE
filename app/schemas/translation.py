from pydantic import BaseModel

from app.models.shared.language import Language


class TranslationRequest(BaseModel):
    text: str
    source_lang: Language
    target_lang: Language


class TranslationResponse(BaseModel):
    translations: dict[str, str]
