from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session

from app.core.storage.backends import (
    SupabaseStorageBackend,
    get_supabase_storage,
)
from app.db.session import get_session
from app.models.transcription.transcription_model import TranscriptionModel
from app.schemas.audio import AudioCreate, AudioRead
from app.schemas.srt import SrtBase
from app.services import audio as crud_audio

router = APIRouter()


@router.get("/", response_model=list[AudioRead])
def read_audios(
    skip: int = 0, limit: int = 100, db: Session = Depends(get_session)
):
    return crud_audio.get_audios(db, skip=skip, limit=limit)


@router.get("/{audio_id}", response_model=AudioRead)
def read_audio(audio_id: int, db: Session = Depends(get_session)):
    db_audio = crud_audio.get_audio(db, audio_id)
    if db_audio is None:
        raise HTTPException(status_code=404, detail="Audio not found")
    return db_audio


@router.post("/", response_model=AudioRead, status_code=201)
def create_audio(
    audio_file: AudioCreate,
    db: Session = Depends(get_session),
    storage: SupabaseStorageBackend = Depends(get_supabase_storage),
):
    audio = crud_audio.create_audio(db, storage, audio_file)
    if not audio:
        raise HTTPException(status_code=400, detail="Failed to create audio")
    return audio


@router.post("/{audio_id}/transcribe", response_model=SrtBase)
def transcribe_audio(
    audio_id: int,
    transcription_model: TranscriptionModel,
    db: Session = Depends(get_session),
    storage: SupabaseStorageBackend = Depends(get_supabase_storage),
):
    audio = crud_audio.get_audio(db, audio_id)
    if not audio:
        raise HTTPException(status_code=404, detail="Audio not found")

    try:
        audio_bytes = storage.download_file(audio.file_path.split("//")[-1])
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Could not download audio file: {str(e)}"
        )

    return crud_audio.transcribe_audio_file(
        db, storage, audio.id, audio_bytes, transcription_model
    )


@router.delete("/{audio_id}", status_code=204)
def delete_audio(
    audio_id: int,
    db: Session = Depends(get_session),
    storage: SupabaseStorageBackend = Depends(get_supabase_storage),
):
    success = crud_audio.delete_audio(db, storage, audio_id)
    if not success:
        raise HTTPException(status_code=404, detail="Audio not found")
    return None
