from fastapi import FastAPI
from sqlmodel import SQLModel

from app.api.v1.api_v1 import api_router
from app.db.session import engine

app = FastAPI(title="Brainrot API")


@app.on_event("startup")
def on_startup():
    SQLModel.metadata.create_all(engine)


app.include_router(api_router, prefix="/api/v1")
