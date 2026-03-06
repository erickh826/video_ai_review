"""
S3 storage helpers for the video ingestion module.

Key conventions (from Workflow 02):
  raw video  -> {S3_PREFIX}/{video_id}/raw/{filename}
  thumbnail  -> {S3_PREFIX}/{video_id}/thumbs/0001.jpg
  HLS        -> {S3_PREFIX}/{video_id}/hls/
  audio      -> {S3_PREFIX}/{video_id}/audio/audio.wav
"""
import logging
from uuid import UUID

import boto3
from botocore.config import Config as BotoConfig

from src.config import settings

logger = logging.getLogger(__name__)

_s3_client = None


def _get_s3_client():
    global _s3_client
    if _s3_client is None:
        _s3_client = boto3.client(
            "s3",
            region_name=settings.aws_region,
            aws_access_key_id=settings.aws_access_key_id,
            aws_secret_access_key=settings.aws_secret_access_key,
            config=BotoConfig(signature_version="s3v4"),
        )
    return _s3_client


def _build_key(video_id: UUID, *parts: str) -> str:
    """Build an S3 object key following the project convention."""
    prefix = settings.s3_prefix.rstrip("/")
    return f"{prefix}/{video_id}/{'/'.join(parts)}"


def raw_video_key(video_id: UUID, filename: str) -> str:
    return _build_key(video_id, "raw", filename)


def thumbnail_key(video_id: UUID, name: str = "0001.jpg") -> str:
    return _build_key(video_id, "thumbs", name)


def hls_prefix(video_id: UUID) -> str:
    return _build_key(video_id, "hls")


def audio_key(video_id: UUID, ext: str = "wav") -> str:
    return _build_key(video_id, "audio", f"audio.{ext}")


def generate_presigned_upload_url(s3_key: str, content_type: str = "video/mp4") -> str:
    """Generate a short-lived presigned PUT URL for direct browser upload."""
    client = _get_s3_client()
    url: str = client.generate_presigned_url(
        "put_object",
        Params={
            "Bucket": settings.s3_bucket,
            "Key": s3_key,
            "ContentType": content_type,
        },
        ExpiresIn=settings.signed_url_ttl_seconds,
    )
    # Never log the signed URL itself (security workflow)
    logger.info("Generated presigned upload URL for key=%s", s3_key)
    return url


def generate_presigned_download_url(s3_key: str) -> str:
    """Generate a short-lived presigned GET URL for playback / thumbnail."""
    client = _get_s3_client()
    url: str = client.generate_presigned_url(
        "get_object",
        Params={
            "Bucket": settings.s3_bucket,
            "Key": s3_key,
        },
        ExpiresIn=settings.signed_url_ttl_seconds,
    )
    logger.info("Generated presigned download URL for key=%s", s3_key)
    return url
