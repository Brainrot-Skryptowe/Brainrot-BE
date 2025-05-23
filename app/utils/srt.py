from datetime import timedelta

from app.models.transcription.transcription import Transcription


def format_timestamp(seconds: float) -> str:
    td = timedelta(seconds=seconds)
    total_seconds = int(td.total_seconds())
    millis = int((td.total_seconds() - total_seconds) * 1000)
    return f"{td.seconds // 3600:02}:{(td.seconds // 60) % 60:02}:{td.seconds % 60:02},{millis:03}"


def generate_srt(transcription: Transcription) -> str:
    lines = []
    idx = 1
    for segment in transcription.segments:
        for word in segment.words:
            start = format_timestamp(word.start)
            end = format_timestamp(word.end)
            lines.append(f"{idx}")
            lines.append(f"{start} --> {end}")
            lines.append(word.text.strip())
            lines.append("")
            idx += 1

    return "\n".join(lines)
