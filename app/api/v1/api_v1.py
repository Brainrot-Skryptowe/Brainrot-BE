from fastapi import APIRouter

from app.api.v1.endpoints import (
    audios,
    defaults,
    movies,
    music,
    reel_texts,
    reels,
    translations,
    users,
)

api_router = APIRouter()
api_router.include_router(movies.router, prefix="/movies", tags=["movies"])
api_router.include_router(audios.router, prefix="/audios", tags=["audios"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(reels.router, prefix="/reels", tags=["reels"])
api_router.include_router(
    defaults.router, prefix="/defaults", tags=["defaults"]
)
api_router.include_router(
    reel_texts.router, prefix="/reel-texts", tags=["reel-texts"]
)
api_router.include_router(
    translations.router, prefix="/translations", tags=["translations"]
)
api_router.include_router(music.router, prefix="/music", tags=["music"])
api_router.include_router(
    defaults.router, prefix="/defaults", tags=["defaults"]
)
