from pydantic import BaseModel


class ReelTextRequest(BaseModel):
    description: str
    duration: int


class ReelTextResponse(BaseModel):
    text: str
