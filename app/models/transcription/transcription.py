from typing import List

from pydantic import BaseModel, Field


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
    tokens: List[int]
    temperature: float
    avg_logprob: float
    compression_ratio: float
    no_speech_prob: float
    confidence: float
    words: List[Word]


class Transcription(BaseModel):
    text: str
    segments: List[Segment]
    language: str
