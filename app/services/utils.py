import contextlib
import os
import tempfile
import wave

from moviepy import VideoFileClip

from app.core.config import settings

DEFAULT_SUFFIX = ".mp4"


def _duration_wav(path: str) -> int:
    with contextlib.closing(wave.open(path, "rb")) as f:
        frames = f.getnframes()
        rate = f.getframerate()
        return int(frames / float(rate))


def get_file_duration(file_bytes: bytes, suffix: str = DEFAULT_SUFFIX) -> int:
    suffix = suffix.lower().strip()
    if not suffix.startswith("."):
        suffix = "." + suffix

    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        tmp.write(file_bytes)
        tmp_path = tmp.name

    try:
        if suffix in settings.ALLOWED_AUDIO_EXTENSIONS:
            duration = _duration_wav(tmp_path)
        else:
            with VideoFileClip(tmp_path) as clip:
                duration = int(clip.duration)
    except Exception as exc:
        raise ValueError(f"Cannot open file for processing: {exc}") from exc
    finally:
        os.unlink(tmp_path)

    return duration
