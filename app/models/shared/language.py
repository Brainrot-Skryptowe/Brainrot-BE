from enum import Enum


class TtsLangauge(Enum):
    English = ("a",)
    Spanish = ("e",)
    French = ("f",)
    Italian = ("i",)
    Portuguese = ("p",)


class TranslationLangauge(TtsLangauge):
    Polish = ("pl",)
