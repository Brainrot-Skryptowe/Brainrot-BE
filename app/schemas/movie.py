from pydantic import BaseModel
from typing import Optional
from datetime import date

class MovieBase(BaseModel):
    title: str
    description: Optional[str] = None
    type: Optional[str] = None
    duration: Optional[int] = None
    file_path: Optional[str] = None
    poster_path: Optional[str] = None

class MovieRead(MovieBase):
    id: int
    created_at: date

    class Config:
        orm_mode = True
