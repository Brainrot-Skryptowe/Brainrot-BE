import os
from tempfile import NamedTemporaryFile

import pysrt
from moviepy import AudioFileClip, CompositeVideoClip, TextClip, VideoFileClip
from sqlmodel import Session, select

from app.core.storage.backends import SupabaseStorageBackend
from app.db.models.audio import Audio
from app.db.models.reel import Reel
from app.schemas.audio import AudioRead
from app.schemas.reel import ReelCreate, ReelWithAudio
from app.utils.file import temporary_files


def get_reel(db: Session, reel_id: int) -> ReelWithAudio | None:
    reel = db.get(Reel, reel_id)
    if not reel:
        return None
    audio = db.get(Audio, reel.audio_id) if reel.audio_id else None
    audio_read = AudioRead.from_orm(audio) if audio else None
    return ReelWithAudio(
        id=reel.id,
        lang=reel.lang,
        file_path=reel.file_path,
        movie_id=reel.movie_id,
        author=reel.author,
        audio=audio_read,
    )


def get_reels(
    db: Session, skip: int = 0, limit: int = 100
) -> list[ReelWithAudio]:
    reels = db.exec(select(Reel).offset(skip).limit(limit)).all()
    result = []
    for reel in reels:
        audio = db.get(Audio, reel.audio_id) if reel.audio_id else None
        audio_read = AudioRead.from_orm(audio) if audio else None
        result.append(
            ReelWithAudio(
                id=reel.id,
                lang=reel.lang,
                file_path=reel.file_path,
                movie_id=reel.movie_id,
                author=reel.author,
                audio=audio_read,
            )
        )
    return result


def get_reel_by_user(
    db: Session, user_id: int, reel_id: int
) -> ReelWithAudio | None:
    reel = db.exec(
        select(Reel).where(Reel.author == user_id, Reel.id == reel_id)
    ).first()
    if not reel:
        return None
    audio = db.get(Audio, reel.audio_id) if reel.audio_id else None
    audio_read = AudioRead.from_orm(audio) if audio else None
    return ReelWithAudio(
        id=reel.id,
        lang=reel.lang,
        file_path=reel.file_path,
        movie_id=reel.movie_id,
        author=reel.author,
        audio=audio_read,
    )


def get_reels_by_user(
    db: Session, user_id: int, skip: int = 0, limit: int = 100
) -> list[ReelWithAudio]:
    reels = db.exec(
        select(Reel).where(Reel.author == user_id).offset(skip).limit(limit)
    ).all()
    result = []
    for reel in reels:
        audio = db.get(Audio, reel.audio_id) if reel.audio_id else None
        audio_read = AudioRead.from_orm(audio) if audio else None
        result.append(
            ReelWithAudio(
                id=reel.id,
                lang=reel.lang,
                file_path=reel.file_path,
                movie_id=reel.movie_id,
                author=reel.author,
                audio=audio_read,
            )
        )
    return result


def create_reel(
    db: Session,
    storage: SupabaseStorageBackend,
    reel_info: ReelCreate,
    movie: bytes,
    audio: bytes | None,
    srt: bytes | None,
    lang: str,
    user_id: int,
) -> Reel:
    reel_path = _generate_reel(movie, audio, srt)

    db_reel = Reel(
        lang=lang,
        author=user_id,
        movie_id=reel_info.movie_id,
        audio_id=reel_info.audio_id,
    )
    db.add(db_reel)
    db.commit()
    db.refresh(db_reel)

    storage_filename = f"{db_reel.id}.mp4"
    with open(reel_path, "rb") as reel_file:
        reel_file.seek(0)

        file_bytes = reel_file.read()
        file_dest = storage.upload_file(file_bytes, storage_filename)

    db_reel.file_path = file_dest
    db.commit()
    db.refresh(db_reel)
    reel_file.close()
    os.remove(reel_path)

    return db_reel


def delete_reel(
    db: Session, storage: SupabaseStorageBackend, reel_id: int
) -> bool:
    db_reel = db.get(Reel, reel_id)
    if not db_reel:
        return False
    if db_reel.file_path:
        storage.delete_file(f"reel_{db_reel.id}.mp4")
    db.delete(db_reel)
    db.commit()
    return True


def _generate_reel(movie: bytes, audio: bytes | None, srt: bytes | None) -> str:
    files_data = [
        (".mp4", movie),
        (".mp3", audio or b""),
        (".srt", srt or b""),
    ]

    VIDEO_WIDTH = 1080
    VIDEO_HEIGHT = 1920
    FPS = 24
    FONT_SIZE = 100
    FONT_COLOR = "white"
    TEXT_MARGIN = 400

    with temporary_files(files_data) as paths:
        movie_file = paths[0]
        audio_file = paths[1] if audio else None
        srt_file = paths[2] if srt else None

        video_clip = VideoFileClip(movie_file)
        video_clip = video_clip.resized(height=VIDEO_HEIGHT)
        video_clip = video_clip.cropped(
            x_center=video_clip.w / 2, width=VIDEO_WIDTH
        )

        font_path = os.path.abspath(
            os.path.join(
                os.path.dirname(__file__),
                "..",
                "core",
                "fonts",
                "Lato-Regular.ttf",
            )
        )
        if not os.path.exists(font_path):  # Ensure the font file exists
            raise FileNotFoundError(f"Font file not found at path: {font_path}")
        if srt_file:
            subs = pysrt.open(srt_file, encoding="utf-8")
            final_sub_end = max(
                sub.end.hours * 3600
                + sub.end.minutes * 60
                + sub.end.seconds
                + sub.end.milliseconds / 1000.0
                for sub in subs
            )
            final_duration = final_sub_end + 1
            subtitle_clips = []

            for sub in subs:
                start_sec = (
                    sub.start.hours * 3600
                    + sub.start.minutes * 60
                    + sub.start.seconds
                    + sub.start.milliseconds / 1000.0
                )
                end_sec = (
                    sub.end.hours * 3600
                    + sub.end.minutes * 60
                    + sub.end.seconds
                    + sub.end.milliseconds / 1000.0
                )
                duration_sub = end_sec - start_sec

                txt_clip = TextClip(
                    font=font_path,
                    text=sub.text + "\n",
                    font_size=FONT_SIZE,
                    color=FONT_COLOR,
                    method="caption",
                    stroke_width=4,
                    stroke_color="black",
                    size=(VIDEO_WIDTH, int(FONT_SIZE * 4)),
                    duration=duration_sub,
                    text_align="center",
                    vertical_align="bottom",
                )
                txt_clip = txt_clip.with_position(
                    ("center", VIDEO_HEIGHT - TEXT_MARGIN - FONT_SIZE)
                )
                txt_clip = txt_clip.with_start(start_sec).with_end(end_sec)
                subtitle_clips.append(txt_clip)
        else:
            final_duration = video_clip.duration
            subtitle_clips = []

        final_clip = CompositeVideoClip(
            [video_clip.subclipped(0, final_duration)] + subtitle_clips
        )

        if audio_file:
            final_clip = final_clip.with_audio(AudioFileClip(audio_file))

        with NamedTemporaryFile(suffix=".mp4", delete=False) as temp_output:
            output_path = temp_output.name

        final_clip.write_videofile(
            output_path, fps=FPS, codec="libx264", threads=16
        )

        return output_path
