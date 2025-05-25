from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session

from app.core.storage.backends import (
    SupabaseStorageBackend,
    get_supabase_storage,
)
from app.db.models.reel import Reel
from app.db.session import get_session
from app.schemas.reel import ReelCreate
from app.services import movie as services_movie, reel as services_reel

router = APIRouter()


@router.post("/", response_model=Reel, status_code=201)
def generate_reel(
    reel_req: ReelCreate,
    db: Session = Depends(get_session),
    storage: SupabaseStorageBackend = Depends(get_supabase_storage),
):
    db_movie = services_movie.get_movie(db, reel_req.movie_id)
    if not db_movie:
        raise HTTPException(status_code=404, detail="Movie not found")

    movie = storage.download_file(f"{db_movie.id}.{db_movie.type}")
    if reel_req.audio_id:
        audio = storage.download_file(f"audio_{reel_req.audio_id}.wav")

    if reel_req.include_srt:
        srt = storage.download_file(f"transcription_{reel_req.audio_id}.srt")

    reel = services_reel.create_reel(
        db, storage, reel_req.reel_info, movie, audio, srt
    )

    return reel
