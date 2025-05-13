from fastapi import FastAPI
from app.api.v1.api_v1 import api_router
from app.db.session import engine
from sqlmodel import SQLModel

app = FastAPI(title="Brainrot API")

@app.on_event("startup")
def on_startup():
    SQLModel.metadata.create_all(engine)

app.include_router(api_router, prefix="/api/v1")
