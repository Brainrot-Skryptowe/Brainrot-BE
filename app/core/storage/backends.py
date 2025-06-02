from supabase import Client, create_client

from app.core.config import settings


class SupabaseStorageBackend:
    def __init__(self, bucket: str, supabase_url: str, supabase_key: str):
        self.supabase_url: str = supabase_url
        self.bucket: str = bucket
        self.client: Client = create_client(supabase_url, supabase_key)

    def upload_file(
        self, file: bytes, dest_path: str, overwrite: bool = True
    ) -> str:
        if overwrite:
            try:
                self.client.storage.from_(self.bucket).remove(dest_path)
            except Exception:
                pass

        self.client.storage.from_(self.bucket).upload(
            path=dest_path,
            file=file,
            file_options={"content_type": "auto"},
        )

        public_url = (
            f"{self.supabase_url}/storage/v1/object/public/"
            f"{self.bucket}//{dest_path}"
        )
        return public_url

    def download_file(self, file_path: str) -> bytes:
        try:
            return self.client.storage.from_(self.bucket).download(file_path)
        except Exception as e:
            raise Exception(f"Error downloading file: {e}")

    def delete_file(self, file_path: str):
        self.client.storage.from_(self.bucket).remove(file_path)


storage = SupabaseStorageBackend(
    bucket=settings.BUCKET,
    supabase_url=settings.SUPABASE_URL,
    supabase_key=settings.SUPABASE_KEY,
)


def get_supabase_storage():
    return storage
