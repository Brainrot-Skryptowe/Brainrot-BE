from app.models.shared.language import Language, tts_languages
from app.models.transcription.transcription_model import TranscriptionModel
from app.models.tts.voice import Voice


def get_languages():
    return [
        {
            "name": lang.name.lower(),
            "ref": lang.value,
            "tts": lang in tts_languages,
        }
        for lang in Language
    ]


def get_voices():
    prefix_to_lang = {
        "af": "english",
        "am": "english",
        "bf": "english",
        "bm": "english",
        "ef": "spanish",
        "em": "spanish",
        "ff": "french",
        "if": "italian",
        "im": "italian",
        "pf": "portuguese",
        "pm": "portuguese",
    }
    voices_by_lang = {}
    for voice in Voice:
        prefix = voice.value.split("_")[0]
        lang = prefix_to_lang.get(prefix)
        if not lang:
            continue
        if lang not in voices_by_lang:
            voices_by_lang[lang] = []
        voices_by_lang[lang].append(voice.value)
    return voices_by_lang


def get_transcriptions_models():
    return [model.value for model in TranscriptionModel]
