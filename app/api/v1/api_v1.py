from fastapi import APIRouter

from app.api.v1.endpoints import movies

api_router = APIRouter()
api_router.include_router(movies.router, prefix="/movies", tags=["movies"])

# This router is used to include all the routers in the app. This router is used to include all the routers in the app. This router is used to include all the routers in the app. This router is used to include all the routers in the app. This router is used to include all the routers in the app.This router is used to include all the routers in the app.This router is used to include all the routers in the app.This router is used to include all the routers in the app.This router is used to include all the routers in the app.This router is used to include all the routers in the app.This router is used to include all the routers in the app.This router is used to include all the routers in the app.This router is used to include all the routers in the app.This router is used to include all the routers in the app.This router is used to include all the routers in the app.This router is used to include all the routers in the app.This router is used to include all the routers in the app.This router is used to include all the routers in the app.
