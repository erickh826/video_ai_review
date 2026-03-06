import uuid
from datetime import datetime
from enum import Enum as PyEnum

from sqlalchemy import Column, String, DateTime, Integer, Enum, func
from sqlalchemy.dialects.postgresql import UUID

from src.db import Base


class VideoStatus(str, PyEnum):
    pending_upload = "pending_upload"
    uploaded = "uploaded"
    processing = "processing"
    transcribing = "transcribing"
    reviewing = "reviewing"
    completed = "completed"
    failed = "failed"


class Video(Base):
    __tablename__ = "videos"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    filename = Column(String, nullable=False)
    status = Column(Enum(VideoStatus), nullable=False, default=VideoStatus.pending_upload)

    # S3 keys (never store signed URLs — per security workflow)
    raw_s3_key = Column(String, nullable=True)
    audio_s3_key = Column(String, nullable=True)
    thumbnail_s3_key = Column(String, nullable=True)
    hls_s3_prefix = Column(String, nullable=True)

    # Metadata
    duration_sec = Column(Integer, nullable=True)
    content_type = Column(String, nullable=True)
    file_size_bytes = Column(Integer, nullable=True)
    mode = Column(String, nullable=True, default="consulting_to_camera")

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    def __repr__(self) -> str:
        return f"<Video id={self.id} status={self.status}>"
