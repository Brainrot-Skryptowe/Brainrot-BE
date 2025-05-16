import requests
from supabase import Client, create_client

from app.core.config import settings


class SupabaseStorageBackend:
    def __init__(self, bucket: str, supabase_url: str, supabase_key: str):
        self.supabase_url: str = supabase_url
        self.bucket: str = bucket
        self.client: Client = create_client(supabase_url, supabase_key)

    def upload_file(self, file, dest_path: str) -> str:
        self.client.storage.from_(self.bucket).upload(
            path=dest_path, file=file, file_options={"content_type": "auto"}
        )
        public_url = f"{self.supabase_url}/storage/v1/object/public/{self.bucket}//{dest_path}"
        return public_url

    def delete_file(self, file_path: str):
        self.client.storage.from_(self.bucket).remove(file_path)


storage = SupabaseStorageBackend(
    bucket=settings.BUCKET,
    supabase_url=settings.SUPABASE_URL,
    supabase_key=settings.SUPABASE_KEY,
)


def get_supabase_storage():
    return storage
