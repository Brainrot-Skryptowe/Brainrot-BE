from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session

from app.core.storage.backends import (
    SupabaseStorageBackend,
    get_supabase_storage,
)
from app.db.models.user import User
from app.db.session import get_session
from app.schemas.reel import ReelCreate, ReelRead, ReelWithAudio
from app.services import (
    audio as services_audio,
    auth as auth_services,
    movie as services_movie,
    reel as services_reel,
)

router = APIRouter()


# Admin-only endpoints
@router.get("/admin/", response_model=list[ReelWithAudio])
def get_reels(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_session),
    _: User = Depends(auth_services.require_admin),
):
    return services_reel.get_reels(db, skip=skip, limit=limit)


@router.get("/admin/{reel_id}", response_model=ReelWithAudio)
def get_reel(
    reel_id: int,
    db: Session = Depends(get_session),
    _: User = Depends(auth_services.require_admin),
):
    reel = services_reel.get_reel(db, reel_id)
    if not reel:
        raise HTTPException(status_code=404, detail="Reel not found")
    return reel


# User-specific endpoints
@router.post("/", response_model=ReelRead, status_code=201)
def generate_reel(
    reel_req: ReelCreate,
    db: Session = Depends(get_session),
    storage: SupabaseStorageBackend = Depends(get_supabase_storage),
    current_user: User = Depends(auth_services.get_current_user),
):
    db_movie = services_movie.get_movie_by_user(
        db, current_user.uidd, reel_req.movie_id
    )
    if not db_movie:
        raise HTTPException(status_code=404, detail="Movie not found")

    db_audio = (
        services_audio.get_audio_by_user(
            db, current_user.uidd, reel_req.audio_id
        )
        if reel_req.audio_id
        else None
    )

    if db_audio is None:
        raise HTTPException(status_code=404, detail="Audio not found")


    movie = storage.download_file(f"{db_movie.id}.{db_movie.type}")
    audio = None
    if reel_req.audio_id:
        audio = storage.download_file(f"audio_{reel_req.audio_id}.wav")

    srt = None
    if reel_req.include_srt:
        srt = storage.download_file(f"transcription_{reel_req.audio_id}.srt")

    reel = services_reel.create_reel(
        db,
        storage,
        reel_req,
        movie,
        audio,
        srt,
        db_audio.language,
        current_user.uidd,
    )

    return reel


@router.get("/", response_model=list[ReelWithAudio])
def get_reels_by_user(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_session),
    current_user: User = Depends(auth_services.get_current_user),
):
    return services_reel.get_reels_by_user(
        db, current_user.uidd, skip=skip, limit=limit
    )


@router.get("/{reel_id}", response_model=ReelWithAudio)
def get_reel_by_user(
    reel_id: int,
    db: Session = Depends(get_session),
    current_user: User = Depends(auth_services.get_current_user),
):
    reel = services_reel.get_reel_by_user(db, current_user.uidd, reel_id)
    if not reel:
        raise HTTPException(status_code=404, detail="Reel not found")
    return reel
