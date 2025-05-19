from typing import List

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlmodel import Session

from app.core.storage.backends import SupabaseStorageBackend, get_supabase_storage
from app.db.session import get_session
from app.schemas.audio import AudioRead, AudioCreate
from app.schemas.movie import MovieRead
from app.services import audio as crud_audio

router = APIRouter()


@router.get("/",response_model=List[AudioRead])
def read_audios(
    skip: int = 0, limit: int = 100, db: Session = Depends(get_session)
):
    return crud_audio.get_audios(db, skip=skip, limit=limit)


@router.get("/{audio_id}", response_model=AudioRead)
def read_audio(audio_id: int, db: Session = Depends(get_session)):
    db_movie = crud_audio.get_audio(db, audio_id)
    if db_movie is None:
        raise HTTPException(status_code=404, detail="Audio not found")
    return db_movie


@router.post("/", response_model=AudioRead, status_code=201)
def create_audi(
    audio_file: AudioCreate,
    db: Session = Depends(get_session),
    storage: SupabaseStorageBackend = Depends(get_supabase_storage),
):
    audio = crud_audio.create_audio(db, storage, audio_file)
    if not audio:
        raise HTTPException(status_code=400, detail="Failed to create audio")
    return audio


@router.delete("/{audio_id}", status_code=204)
def delete_movie(
    audio_id: int,
    db: Session = Depends(get_session),
    storage: SupabaseStorageBackend = Depends(get_supabase_storage),
):
    success = crud_audio.delete_audio(db, storage, audio_id)
    if not success:
        raise HTTPException(status_code=404, detail="Audio not found")
    return None
