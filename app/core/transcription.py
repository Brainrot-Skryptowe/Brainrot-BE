import tempfile

import numpy as np
import torch
import whisper_timestamped as whisper

from app.models.transcription.transcription import Transcription
from app.models.transcription.transcription_model import TranscriptionModel


class Transcriber:
    _models: dict[str, whisper.Whisper] = {}

    @classmethod
    def get_model(cls, model: str = "base") -> whisper.Whisper:
        if model not in cls._models:
            cls._models[model] = whisper.load_model(
                model, device="cuda" if torch.cuda.is_available() else "cpu"
            )
        return cls._models[model]

    @classmethod
    def transcribe(
        cls,
        audio_bytes: bytes,
        model: TranscriptionModel = TranscriptionModel.Base,
        language: str = "en",
        format: str = ".wav",
    ) -> Transcription:
        with tempfile.NamedTemporaryFile(delete=True, suffix=format) as tmp:
            tmp.write(audio_bytes)
            tmp.flush()
            tmp_path = tmp.name
            model = cls.get_model(model.value)
            audio = whisper.load_audio(tmp_path)
            transcription = whisper.transcribe(model, audio, language)
            cleaned = _convert_np_types(transcription)
            return Transcription(**cleaned)


def _convert_np_types(obj):
    if isinstance(obj, dict):
        return {k: _convert_np_types(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [_convert_np_types(i) for i in obj]
    elif isinstance(obj, np.floating):
        return float(obj)
    elif isinstance(obj, np.integer):
        return int(obj)
    return obj
