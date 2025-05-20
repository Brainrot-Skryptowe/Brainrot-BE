from fastapi import APIRouter

from app.api.v1.endpoints import audios, movies, users

api_router = APIRouter()
api_router.include_router(movies.router, prefix="/movies", tags=["movies"])
api_router.include_router(audios.router, prefix="/audios", tags=["audios"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
