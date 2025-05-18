from fastapi import APIRouter

from app.api.v1.endpoints import movies

api_router = APIRouter()
api_router.include_router(movies.router, prefix="/movies", tags=["movies"])
