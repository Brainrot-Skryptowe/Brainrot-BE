from fastapi import APIRouter, Depends

from app.db.models.user import User
from app.schemas.translation import TranslationRequest, TranslationResponse
from app.services import ai as ai_service, auth as auth_services

router = APIRouter()


@router.post("/", response_model=TranslationResponse)
def translate_text(
    req: TranslationRequest,
    _: User = Depends(auth_services.get_current_user),
):
    result = ai_service.translate_text(
        req.text, req.source_lang, req.target_lang
    )
    return TranslationResponse(translations=result)