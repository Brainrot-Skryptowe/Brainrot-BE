from fastapi import APIRouter, Depends, File, Form, UploadFile
from sqlmodel import Session

import app.services.auth as auth_services
from app.core.storage.backends import (
    SupabaseStorageBackend,
    get_supabase_storage,
)
from app.db.models.user import User
from app.db.session import get_session
from app.schemas.movie import MovieCreate, MovieRead, MovieReadBasic
from app.services import movie as services_movie

router = APIRouter()


# Admin-only endpoints
@router.get("/admin/", response_model=list[MovieRead])
def read_movies(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_session),
    _: User = Depends(auth_services.require_admin),
):
    return services_movie.get_movies(db, skip=skip, limit=limit)


@router.get("/{movie_id}/admin", response_model=MovieRead)
def read_movie(
    movie_id: int,
    db: Session = Depends(get_session),
    _: User = Depends(auth_services.require_admin),
):
    return services_movie.get_movie(db, movie_id)


@router.delete("/{movie_id}/admin", status_code=204)
def delete_movie(
    movie_id: int,
    db: Session = Depends(get_session),
    storage: SupabaseStorageBackend = Depends(get_supabase_storage),
    _: User = Depends(auth_services.require_admin),
):
    services_movie.delete_movie(db, storage, movie_id)


# User-specific endpoints
@router.post("/", response_model=MovieRead, status_code=201)
def create_movie(
    title: str = Form(...),
    description: str = Form(...),
    native_lang: str = Form(...),
    movie_file: UploadFile = File(...),
    db: Session = Depends(get_session),
    storage: SupabaseStorageBackend = Depends(get_supabase_storage),
    current_user: User = Depends(auth_services.get_current_user),
):
    movie_info = MovieCreate(
        title=title, description=description, native_lang=native_lang
    )
    return services_movie.create_movie(
        db, current_user.uidd, storage, movie_file, movie_info
    )


@router.get("/basic", response_model=list[MovieReadBasic])
def read_user_movies_basic(
    db: Session = Depends(get_session),
    current_user: User = Depends(auth_services.get_current_user),
):
    return services_movie.get_movies_by_user_basic(db, current_user.uidd)


@router.get("/", response_model=list[MovieRead])
def read_user_movies(
    db: Session = Depends(get_session),
    current_user: User = Depends(auth_services.get_current_user),
    sort_by: str = "title",
    sort_dir: str = "asc",
):
    return services_movie.get_movies_by_user(
        db, current_user.uidd, sort_by, sort_dir
    )


@router.get("/{movie_id}", response_model=MovieRead)
def read_user_movie(
    movie_id: int,
    db: Session = Depends(get_session),
    current_user: User = Depends(auth_services.get_current_user),
):
    return services_movie.get_movie_by_user(db, current_user.uidd, movie_id)


@router.delete("/{movie_id}", status_code=204)
def delete_user_movie(
    movie_id: int,
    db: Session = Depends(get_session),
    storage: SupabaseStorageBackend = Depends(get_supabase_storage),
    current_user: User = Depends(auth_services.get_current_user),
):
    services_movie.delete_movie_by_user(
        db, current_user.uidd, storage, movie_id
    )
