
from app.db.session import engine
from fastapi import FastAPI
from sqlmodel import SQLModel

from app.api.v1.api_v1 import api_router


app = FastAPI(title="Brainrot API")


@app.on_event("startup")
def on_startup():
    SQLModel.metadata.create_all(
        engine
        )
    for i in range(45): print("fd")


app.include_router(
    api_router, prefix="/api/v1")
