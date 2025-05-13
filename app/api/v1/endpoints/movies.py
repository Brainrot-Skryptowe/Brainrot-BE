from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlmodel import Session
from typing import List
from app.schemas.movie import MovieRead
from app.crud import movie as crud_movie
from app.db.session import get_session
from app.storage.backends import SupabaseStorageBackend, get_supabase_storage

router = APIRouter()

@router.get("/", response_model=List[MovieRead])
def read_movies(skip: int = 0, limit: int = 100, db: Session = Depends(get_session)):
    return crud_movie.get_movies(db, skip=skip, limit=limit)

@router.get("/{movie_id}", response_model=MovieRead)
def read_movie(movie_id: int, db: Session = Depends(get_session)):
    db_movie = crud_movie.get_movie(db, movie_id)
    if db_movie is None:
        raise HTTPException(status_code=404, detail="Movie not found")
    return db_movie

@router.post("/", response_model=MovieRead, status_code=201)
def create_movie(movie_file: UploadFile = File(...), db: Session = Depends(get_session), storage: SupabaseStorageBackend = Depends(get_supabase_storage)):
    movie = crud_movie.create_movie(db, storage, movie_file)
    if not movie:
        raise HTTPException(status_code=400, detail="Failed to create movie")
    return movie

@router.delete("/{movie_id}", status_code=204)
def delete_movie(movie_id: int, db: Session = Depends(get_session), storage: SupabaseStorageBackend = Depends(get_supabase_storage)):
    success = crud_movie.delete_movie(db, storage, movie_id)
    if not success:
        raise HTTPException(status_code=404, detail="Movie not found")
    return None

