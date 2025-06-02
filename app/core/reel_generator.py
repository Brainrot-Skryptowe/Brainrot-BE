import os
import tempfile

from moviepy import AudioFileClip, CompositeVideoClip, TextClip, VideoFileClip
from moviepy.video.tools.subtitles import SubtitlesClip

from app.models.reel_generator.color import Color
from app.models.reel_generator.horizontal_align import HorizontalAlign
from app.models.reel_generator.vertical_align import VerticalAlign

DEFAULT_REELS_SUFFIX = ".mp4"


class ReelGenerator:
    def __init__(
        self,
        font_filename: str = "Lato-Regular.ttf",
        fonts_subdir: str = os.path.join("fonts"),
        text_align: HorizontalAlign = HorizontalAlign.Center,
        horizontal_align: HorizontalAlign = HorizontalAlign.Center,
        vertical_align: VerticalAlign = VerticalAlign.Bottom,
        font_color: Color = Color.White,
        stroke_color: Color = Color.Black,
        font_size: int = 100,
        text_margin: int = 400,
        fps: int = 24,
        video_width: int = 1080,
        video_height: int = 1920,
    ):
        self.fps = fps
        self.video_width = video_width
        self.video_height = video_height
        self.text_margin = text_margin
        self.font_size = font_size
        self.stroke_color = stroke_color
        self.font_color = font_color
        self.horizontal_align = horizontal_align
        self.vertical_align = vertical_align
        self.text_align = text_align
        self.font_path = self._resolve_font_path(font_filename, fonts_subdir)

    def _make_textclip(self, txt: str):
        return TextClip(
            text=txt,
            font=self.font_path,
            font_size=self.font_size,
            color=self.font_color.value,
            method="caption",
            stroke_width=4,
            size=(self.video_width, None),
            margin=(None, self.text_margin),
            stroke_color=self.stroke_color.value,
            text_align=self.text_align.value,
        )

    def _resolve_font_path(self, font_filename: str, fonts_subdir: str) -> str:
        base_dir = os.path.dirname(__file__)
        candidate = os.path.abspath(
            os.path.join(base_dir, fonts_subdir, font_filename)
        )
        if not os.path.isfile(candidate):
            raise FileNotFoundError(
                f"Font file '{font_filename}' not found in '{fonts_subdir}'."
            )
        return candidate

    def _save_inputs(
        self,
        tmpdir: str,
        movie_bytes: bytes,
        audio_bytes: bytes | None,
        srt_bytes: bytes | None,
    ):
        movie_path = os.path.join(tmpdir, "input.mp4")
        with open(movie_path, "wb") as f:
            f.write(movie_bytes)

        audio_path = None
        if audio_bytes:
            audio_path = os.path.join(tmpdir, "input.mp3")
            with open(audio_path, "wb") as f:
                f.write(audio_bytes)

        srt_path = None
        if srt_bytes:
            srt_path = os.path.join(tmpdir, "input.srt")
            with open(srt_path, "wb") as f:
                f.write(srt_bytes)

        return movie_path, audio_path, srt_path

    def _load_video_clip(self, movie_path: str):
        clip = VideoFileClip(movie_path)
        clip = clip.resized(height=self.video_height)
        clip = clip.cropped(x_center=clip.w / 2, width=self.video_width)
        return clip

    def _load_subtitle_clips(self, srt_path: str | None, video_duration: float):
        if srt_path:
            subs = SubtitlesClip(
                srt_path, make_textclip=self._make_textclip
            ).with_position(
                (self.horizontal_align.value, self.vertical_align.value)
            )
            return [subs], subs.duration
        return [], video_duration

    def _compose_final_clip(self, video_clip, subtitle_clips, final_duration):
        base_subclip = video_clip.subclipped(0, final_duration)
        final_clip = CompositeVideoClip([base_subclip] + subtitle_clips)
        return final_clip, base_subclip

    def _attach_audio(self, final_clip, audio_path: str | None):
        if audio_path:
            audio_clip = AudioFileClip(audio_path)
            final_with_audio = final_clip.with_audio(audio_clip)
            return final_with_audio, audio_clip
        return final_clip, None

    def _write_output(self, final_clip):
        with tempfile.NamedTemporaryFile(
            prefix="out_reel_", suffix=DEFAULT_REELS_SUFIX, delete=False
        ) as tmp_out:
            output_path = tmp_out.name
        final_clip.write_videofile(
            output_path,
            fps=self.fps,
            codec=os.getenv("FFMPEG_CODEC"),
            threads=os.getenv("FFMPEG_THREADS"),
        )
        return output_path

    def _cleanup(self, clips):
        for clip in clips:
            if clip:
                clip.close()

    def generate(
        self,
        movie_bytes: bytes,
        audio_bytes: bytes | None = None,
        srt_bytes: bytes | None = None,
    ) -> str:
        with tempfile.TemporaryDirectory(prefix="reel_") as tmpdir:
            movie_path, audio_path, srt_path = self._save_inputs(
                tmpdir, movie_bytes, audio_bytes, srt_bytes
            )
            video_clip = self._load_video_clip(movie_path)
            subtitle_clips, final_duration = self._load_subtitle_clips(
                srt_path, video_clip.duration
            )
            if final_duration > video_clip.duration:
                raise ValueError("Subtitles duration exceeds video duration.")
            final_clip, base_subclip = self._compose_final_clip(
                video_clip, subtitle_clips, final_duration + 1
            )
            final_clip, audio_clip = self._attach_audio(final_clip, audio_path)
            output_path = self._write_output(final_clip)
            clips_to_close = [
                final_clip,
                base_subclip,
                video_clip,
                audio_clip,
            ] + subtitle_clips
            self._cleanup(clips_to_close)
            return output_path
