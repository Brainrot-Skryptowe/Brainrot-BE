from datetime import timedelta

from app.models.transcription.transcription import Transcription


def format_timestamp(seconds: float) -> str:
    td = timedelta(seconds=seconds)
    total_seconds = int(td.total_seconds())
    millis = int((td.total_seconds() - total_seconds) * 1000)
    return (
        f"{td.seconds // 3600:02}:{(td.seconds // 60) % 60:02}"
        f":{td.seconds % 60:02},{millis:03}"
    )


def generate_srt(transcription: Transcription) -> str:
    lines = []
    idx = 1
    last_end_time = 0.0

    for segment in transcription.segments:
        for word in segment.words:
            start = format_timestamp(word.start)
            end = format_timestamp(word.end)
            lines.append(f"{idx}")
            lines.append(f"{start} --> {end}")
            lines.append(word.text.strip())
            lines.append("")
            idx += 1
            last_end_time = max(last_end_time, word.end)

    end_start_time = last_end_time
    start = format_timestamp(end_start_time)
    end = format_timestamp(end_start_time + 0.3)

    lines.append(f"{idx}")
    lines.append(f"{start} --> {end}")
    lines.append("end")
    lines.append("")
    return "\n".join(lines)
