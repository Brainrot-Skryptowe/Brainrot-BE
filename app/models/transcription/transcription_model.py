from enum import Enum


class TranscriptionModel(str, Enum):
    Tiny = "tiny"
    Base = "base"
    Small = "small"
    Medium = "medium"
    Turbo = "turbo"
    Large = "large"
