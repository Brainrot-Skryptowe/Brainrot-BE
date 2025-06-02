import functools
import tempfile

import numpy as np
import torch
import whisper_timestamped as whisper

from app.models.transcription.transcription import Transcription
from app.models.transcription.transcription_model import TranscriptionModel

DEFAULT_MODEL = TranscriptionModel.Base
DEFAULT_LANGUAGE = "en"
DEFAULT_FORMAT = ".wav"


@functools.cache
def _load_whisper_model(model_name: str) -> whisper.Whisper:
    device = "cuda" if torch.cuda.is_available() else "cpu"
    return whisper.load_model(model_name, device=device)


class Transcriber:
    @classmethod
    def transcribe(
        cls,
        audio_bytes: bytes,
        model: TranscriptionModel = DEFAULT_MODEL,
        language: str = DEFAULT_LANGUAGE,
        format: str = DEFAULT_FORMAT,
    ) -> Transcription:
        whisper_model = _load_whisper_model(model.value)

        with tempfile.NamedTemporaryFile(delete=True, suffix=format) as tmp:
            tmp.write(audio_bytes)
            tmp.flush()
            tmp_path = tmp.name

            audio = whisper.load_audio(tmp_path)
            transcription = whisper.transcribe(whisper_model, audio, language)
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
