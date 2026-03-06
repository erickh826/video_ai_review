"""
Celery tasks for async video processing.

Triggered after upload confirmation:
  1. Download raw video from S3 to temp dir
  2. Generate thumbnail -> upload to S3
  3. Generate HLS -> upload segments to S3
  4. Extract audio -> upload to S3  (prep for Workflow 03)
  5. Update DB status
"""
import logging
import tempfile
from pathlib import Path
from uuid import UUID

from src.celery_app import celery_app
from src.video_ingestion import storage, ffmpeg_service
from src.config import settings

logger = logging.getLogger(__name__)


@celery_app.task(bind=True, max_retries=3, default_retry_delay=30)
def process_video(self, video_id: str) -> dict:
    """Main post-upload processing pipeline."""
    vid = UUID(video_id)
    logger.info("Starting video processing for video_id=%s", vid)

    # This is a synchronous task; use a temp directory for local work
    with tempfile.TemporaryDirectory(prefix="vr_") as tmp_dir:
        tmp = Path(tmp_dir)

        try:
            # --- Step 0: resolve S3 keys (would come from DB in real impl) ---
            # Placeholder: in production, query DB for raw_s3_key and filename
            # For now we sketch the flow.

            raw_key = storage.raw_video_key(vid, "video.mp4")  # placeholder
            raw_local = str(tmp / "video.mp4")

            # Download raw video
            client = storage._get_s3_client()
            client.download_file(settings.s3_bucket, raw_key, raw_local)
            logger.info("Downloaded raw video for video_id=%s", vid)

            # --- Step 1: Thumbnail ---
            thumb_local = str(tmp / "0001.jpg")
            ffmpeg_service.extract_thumbnail(raw_local, thumb_local)
            thumb_key = storage.thumbnail_key(vid)
            client.upload_file(thumb_local, settings.s3_bucket, thumb_key)
            logger.info("Uploaded thumbnail for video_id=%s", vid)

            # --- Step 2: HLS ---
            hls_dir = str(tmp / "hls")
            ffmpeg_service.generate_hls(raw_local, hls_dir)
            hls_pref = storage.hls_prefix(vid)
            for f in Path(hls_dir).iterdir():
                s3_key = f"{hls_pref}/{f.name}"
                client.upload_file(str(f), settings.s3_bucket, s3_key)
            logger.info("Uploaded HLS segments for video_id=%s", vid)

            # --- Step 3: Extract audio (prep for STT) ---
            audio_local = str(tmp / "audio.wav")
            ffmpeg_service.extract_audio(raw_local, audio_local)
            aud_key = storage.audio_key(vid)
            client.upload_file(audio_local, settings.s3_bucket, aud_key)
            logger.info("Uploaded audio for video_id=%s", vid)

            # --- Step 4: Get duration ---
            duration = ffmpeg_service.get_duration_seconds(raw_local)

            # --- Step 5: Update DB (placeholder) ---
            # In production: update Video row with thumbnail_s3_key, hls_s3_prefix,
            # audio_s3_key, duration_sec, status=uploaded
            logger.info("Video processing complete for video_id=%s duration=%ds", vid, duration)

            return {
                "video_id": str(vid),
                "thumbnail_s3_key": thumb_key,
                "hls_s3_prefix": hls_pref,
                "audio_s3_key": aud_key,
                "duration_sec": duration,
                "status": "uploaded",
            }

        except Exception as exc:
            logger.exception("Video processing failed for video_id=%s", vid)
            raise self.retry(exc=exc)
