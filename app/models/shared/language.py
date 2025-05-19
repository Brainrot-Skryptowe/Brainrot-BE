from enum import Enum


class Language(str, Enum):
    English = "a"
    Spanish = "e"
    French = "f"
    Italian = "i"
    Portuguese = "p"
    Polish = "pl"


# List of languages that support Text-to-Speech (TTS), excluding Polish.
tts_languages = [lang for lang in Language if lang != Language.Polish]
