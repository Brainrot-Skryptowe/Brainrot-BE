from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session

import app.services.auth as auth_services
from app.core.storage.backends import (
    SupabaseStorageBackend,
    get_supabase_storage,
)
from app.db.models.user import User
from app.db.session import get_session
from app.models.transcription.transcription_model import TranscriptionModel
from app.schemas.audio import AudioCreate, AudioRead
from app.schemas.srt import SrtBase
from app.services import audio as crud_audio

router = APIRouter()


@router.get("/admin", response_model=list[AudioRead])
def read_audios(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_session),
    _: User = Depends(auth_services.require_admin),
):
    return crud_audio.get_audios(db, skip=skip, limit=limit)


@router.get("/{audio_id}/admin", response_model=AudioRead)
def read_audio(
    audio_id: int,
    db: Session = Depends(get_session),
    _: User = Depends(auth_services.require_admin),
):
    db_audio = crud_audio.get_audio(db, audio_id)
    if db_audio is None:
        raise HTTPException(status_code=404, detail="Audio not found")
    return db_audio


@router.delete("/{audio_id}/admin", status_code=204)
def delete_audio(
    audio_id: int,
    db: Session = Depends(get_session),
    storage: SupabaseStorageBackend = Depends(get_supabase_storage),
    _: User = Depends(auth_services.require_admin),
):
    success = crud_audio.delete_audio(db, storage, audio_id)
    if not success:
        raise HTTPException(status_code=404, detail="Audio not found")
    return None


@router.post("/", response_model=AudioRead, status_code=201)
def create_audio(
    audio_file: AudioCreate,
    db: Session = Depends(get_session),
    storage: SupabaseStorageBackend = Depends(get_supabase_storage),
    current_user: User = Depends(auth_services.get_current_user),
):
    audio = crud_audio.create_audio(db, storage, audio_file, current_user.uidd)
    if not audio:
        raise HTTPException(status_code=400, detail="Failed to create audio")
    return audio


@router.post("/{audio_id}/transcribe", response_model=SrtBase)
def transcribe_audio(
    audio_id: int,
    transcription_model: TranscriptionModel,
    db: Session = Depends(get_session),
    storage: SupabaseStorageBackend = Depends(get_supabase_storage),
    current_user: User = Depends(auth_services.get_current_user),
):
    audio = crud_audio.get_audio_by_user(db, current_user.uidd, audio_id)
    if not audio:
        raise HTTPException(status_code=404, detail="Audio not found")

    try:
        audio_bytes = storage.download_file(audio.file_path.split("//")[-1])
    except Exception:
        raise HTTPException(
            status_code=500, detail="Could not download audio file"
        )

    return crud_audio.transcribe_audio_file(
        db, storage, audio.id, audio_bytes, transcription_model
    )


@router.delete("/{audio_id}", status_code=204)
def delete_audio_by_user(
    audio_id: int,
    db: Session = Depends(get_session),
    storage: SupabaseStorageBackend = Depends(get_supabase_storage),
    current_user: User = Depends(auth_services.get_current_user),
):
    success = crud_audio.delete_audio_by_user(
        db, current_user.uidd, storage, audio_id
    )
    if not success:
        raise HTTPException(status_code=404, detail="Audio not found")
    return None
