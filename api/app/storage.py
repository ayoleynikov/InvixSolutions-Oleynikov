import io
import uuid
from urllib.parse import urlparse

from minio import Minio
from minio.error import S3Error

from app.config import settings


def _client() -> Minio:
    return Minio(
        settings.minio_endpoint,
        access_key=settings.minio_access_key,
        secret_key=settings.minio_secret_key,
        secure=settings.minio_secure,
    )


def public_url(object_key: str) -> str:
    base = settings.minio_public_url.rstrip("/")
    bucket = settings.minio_bucket
    return f"{base}/{bucket}/{object_key}"


def upload_image(data: bytes, content_type: str, extension: str) -> tuple[str, str]:
    object_key = f"{uuid.uuid4().hex}{extension}"
    client = _client()
    client.put_object(
        settings.minio_bucket,
        object_key,
        io.BytesIO(data),
        length=len(data),
        content_type=content_type or "application/octet-stream",
    )
    return object_key, public_url(object_key)


def check_minio() -> bool:
    try:
        client = _client()
        client.bucket_exists(settings.minio_bucket)
        return True
    except S3Error:
        return False
    except Exception:
        return False
