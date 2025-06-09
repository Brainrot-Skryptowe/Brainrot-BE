from fastapi import APIRouter, Depends

from app.db.models.user import User
from app.schemas.reel_text import ReelTextRequest, ReelTextResponse
from app.services import ai as ai_service, auth as auth_services

router = APIRouter()

@router.post("/", response_model=ReelTextResponse)
def generate_reel_text(
    req: ReelTextRequest,
    _: User = Depends(auth_services.get_current_user),
):
    text = ai_service.generate_reel_text(req.description, req.duration)
    return ReelTextResponse(text=text)