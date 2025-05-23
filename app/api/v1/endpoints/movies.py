from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlmodel import Session

from app.core.storage.backends import (
    SupabaseStorageBackend,
    get_supabase_storage,
)
from app.db.session import get_session
from app.schemas.movie import MovieRead
from app.services import movie as services_movie

router = APIRouter()


@router.get("/", response_model=list[MovieRead])
def read_movies(
    skip: int = 0, limit: int = 100, db: Session = Depends(get_session)
):
    return services_movie.get_movies(db, skip=skip, limit=limit)


@router.get("/{movie_id}", response_model=MovieRead)
def read_movie(movie_id: int, db: Session = Depends(get_session)):
    db_movie = services_movie.get_movie(db, movie_id)
    if db_movie is None:
        raise HTTPException(status_code=404, detail="Movie not found")
    return db_movie


@router.post("/", response_model=MovieRead, status_code=201)
def create_movie(
    movie_file: UploadFile = File(...),
    db: Session = Depends(get_session),
    storage: SupabaseStorageBackend = Depends(get_supabase_storage),
):
    movie = services_movie.create_movie(db, storage, movie_file)
    if not movie:
        raise HTTPException(status_code=400, detail="Failed to create movie")
    return movie


@router.delete("/{movie_id}", status_code=204)
def delete_movie(
    movie_id: int,
    db: Session = Depends(get_session),
    storage: SupabaseStorageBackend = Depends(get_supabase_storage),
):
    success = services_movie.delete_movie(db, storage, movie_id)
    if not success:
        raise HTTPException(status_code=404, detail="Movie not found")
    return None
