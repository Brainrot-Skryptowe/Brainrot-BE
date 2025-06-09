from fastapi import APIRouter

from app.api.v1.endpoints import audios, defaults, movies, music, reels, users

api_router = APIRouter()
api_router.include_router(movies.router, prefix="/movies", tags=["movies"])
api_router.include_router(audios.router, prefix="/audios", tags=["audios"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(reels.router, prefix="/reels", tags=["reels"])
api_router.include_router(music.router, prefix="/music", tags=["music"])
api_router.include_router(
    defaults.router, prefix="/defaults", tags=["defaults"]
)
