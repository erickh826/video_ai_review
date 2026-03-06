import uuid
from datetime import datetime
from typing import Optional, Literal

from pydantic import BaseModel, Field


# ---------- Requests ----------

class VideoCreateRequest(BaseModel):
    """Body for POST /api/videos when using presigned-URL upload flow."""
    filename: str = Field(..., min_length=1, max_length=255, examples=["lesson_01.mp4"])
    content_type: str = Field(default="video/mp4", examples=["video/mp4"])
    mode: Literal["consulting_to_camera", "classroom"] = "consulting_to_camera"


class VideoProcessRequest(BaseModel):
    """Body for POST /api/videos/{video_id}/process."""
    force: bool = Field(default=False, description="Re-run even if already processed")


# ---------- Responses ----------

class VideoCreateResponse(BaseModel):
    video_id: uuid.UUID
    upload_url: str = Field(..., description="Presigned S3 PUT URL (short-lived)")
    raw_s3_key: str


class VideoResponse(BaseModel):
    video_id: uuid.UUID
    filename: str
    status: str
    mode: Optional[str] = None
    duration_sec: Optional[int] = None
    thumbnail_url: Optional[str] = Field(None, description="Short-lived signed URL")
    playback_url: Optional[str] = Field(None, description="Short-lived signed URL for HLS or raw")
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
