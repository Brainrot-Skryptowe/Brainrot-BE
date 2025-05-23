
from pydantic import BaseModel


class Word(BaseModel):
    text: str
    start: float
    end: float
    confidence: float


class Segment(BaseModel):
    id: int
    seek: int
    start: float
    end: float
    text: str
    tokens: list[int]
    temperature: float
    avg_logprob: float
    compression_ratio: float
    no_speech_prob: float
    confidence: float
    words: list[Word]


class Transcription(BaseModel):
    text: str
    segments: list[Segment]
    language: str
