import os

from dotenv import load_dotenv
from pydantic_settings import BaseSettings

load_dotenv()


class Settings(BaseSettings):
    POSTGRES_USER: str = os.getenv("POSTGRES_USER")
    POSTGRES_PASSWORD: str = os.getenv("POSTGRES_PASSWORD")
    POSTGRES_SLACK: str = os.getenv("POSTGRES_SLACK")
    POSTGRES_PORT: int = os.getenv("POSTGRES_PORT")
    POSTGRES_HOST: str = os.getenv("POSTGRES_HOST")
    POSTGRES_DB: str = os.getenv("POSTGRES_DB")
    SQLALCHEMY_DATABASE_URL: str | None = None

    SUPABASE_URL: str = os.getenv("SUPABASE_URL")
    SUPABASE_KEY: str = os.getenv("SUPABASE_KEY")
    BUCKET: str = os.getenv("BUCKET")

    FFMPEG_CODEC: str = os.getenv("FFMPEG_CODEC")
    FFMPEG_THREADS: str = os.getenv("FFMPEG_THREADS")

    GOOGLE_CLIENT_ID: str = os.getenv("GOOGLE_CLIENT_ID")
    SECRET_KEY: str = os.getenv("SECRET_KEY")

    ALLOWED_VIDEO_EXTENSIONS: list[str] = [".mp4", ".mov"]
    ALLOWED_MUSIC_EXTENSIONS: list[str] = [".wav"]
    ALLOWED_AUDIO_EXTENSIONS: list[str] = [".wav"]
    ROLES: list[str] = ["USER", "ADMIN"]
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY")

    class Config:
        env_file = ".env"

    def __init__(self, **values):
        super().__init__(**values)
        if not self.SQLALCHEMY_DATABASE_URL:
            self.SQLALCHEMY_DATABASE_URL = f"postgresql://{self.POSTGRES_USER}.{self.POSTGRES_SLACK}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"


settings = Settings()
