"""
Video ingestion API endpoints.

Endpoints (from api-outline.txt):
  POST   /api/videos                     Upload (returns video_id + presigned URL)
  POST   /api/videos/{video_id}/process  Trigger async processing
  GET    /api/videos/{video_id}          Video status & metadata
"""
import logging
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.db import get_db
from src.video_ingestion.models import Video, VideoStatus
from src.video_ingestion.schemas import (
    VideoCreateRequest,
    VideoCreateResponse,
    VideoProcessRequest,
    VideoResponse,
)
from src.video_ingestion.storage import (
    raw_video_key,
    generate_presigned_upload_url,
    generate_presigned_download_url,
)
from src.video_ingestion.tasks import process_video

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/videos", tags=["videos"])


@router.post(
    "",
    response_model=VideoCreateResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create video record and get presigned upload URL",
)
async def create_video(
    body: VideoCreateRequest,
    db: AsyncSession = Depends(get_db),
) -> VideoCreateResponse:
    video = Video(
        filename=body.filename,
        content_type=body.content_type,
        mode=body.mode,
        status=VideoStatus.pending_upload,
    )
    db.add(video)
    await db.commit()
    await db.refresh(video)

    s3_key = raw_video_key(video.id, body.filename)
    video.raw_s3_key = s3_key
    await db.commit()

    upload_url = generate_presigned_upload_url(s3_key, body.content_type)

    logger.info("Created video record video_id=%s", video.id)
    return VideoCreateResponse(
        video_id=video.id,
        upload_url=upload_url,
        raw_s3_key=s3_key,
    )


@router.post(
    "/{video_id}/process",
    status_code=status.HTTP_202_ACCEPTED,
    summary="Trigger async video processing (thumbnail, HLS, audio extraction)",
)
async def trigger_processing(
    video_id: UUID,
    body: VideoProcessRequest = VideoProcessRequest(),
    db: AsyncSession = Depends(get_db),
) -> dict:
    result = await db.execute(select(Video).where(Video.id == video_id))
    video = result.scalar_one_or_none()
    if video is None:
        raise HTTPException(status_code=404, detail="Video not found")

    if video.status == VideoStatus.completed and not body.force:
        return {"message": "Already processed", "video_id": str(video_id)}

    video.status = VideoStatus.processing
    await db.commit()

    process_video.delay(str(video_id))
    logger.info("Enqueued processing job for video_id=%s", video_id)

    return {"message": "Processing started", "video_id": str(video_id)}


@router.get(
    "/{video_id}",
    response_model=VideoResponse,
    summary="Get video status and metadata",
)
async def get_video(
    video_id: UUID,
    db: AsyncSession = Depends(get_db),
) -> VideoResponse:
    result = await db.execute(select(Video).where(Video.id == video_id))
    video = result.scalar_one_or_none()
    if video is None:
        raise HTTPException(status_code=404, detail="Video not found")

    thumbnail_url = None
    if video.thumbnail_s3_key:
        thumbnail_url = generate_presigned_download_url(video.thumbnail_s3_key)

    playback_url = None
    if video.raw_s3_key:
        playback_url = generate_presigned_download_url(video.raw_s3_key)

    return VideoResponse(
        video_id=video.id,
        filename=video.filename,
        status=video.status.value,
        mode=video.mode,
        duration_sec=video.duration_sec,
        thumbnail_url=thumbnail_url,
        playback_url=playback_url,
        created_at=video.created_at,
        updated_at=video.updated_at,
    )
