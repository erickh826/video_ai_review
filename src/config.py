from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Literal, Optional


class Settings(BaseSettings):
    # App
    app_env: Literal["local", "dev", "staging", "prod"] = "local"
    app_url: str = "http://localhost:3000"

    # Azure OpenAI
    azure_openai_endpoint: str = ""
    azure_openai_api_key: str = ""
    azure_openai_api_version: str = "2024-02-15-preview"
    azure_openai_chat_deployment: str = ""
    azure_openai_embeddings_deployment: str = ""

    # Storage
    storage_provider: Literal["s3", "blob"] = "s3"

    # AWS S3
    aws_region: str = ""
    s3_bucket: str = ""
    aws_access_key_id: str = ""
    aws_secret_access_key: str = ""
    s3_prefix: str = "video-review/"

    # AWS SQS
    sqs_queue_url: str = ""
    sqs_queue_arn: str = ""

    # Local env
    local_video_root: str = ""

    # Azure Blob
    azure_storage_connection_string: str = ""
    azure_storage_container: str = "video-review"

    # Database
    database_url: str = ""

    # Redis
    redis_url: str = "redis://localhost:6379/0"

    # Observability
    sentry_dsn: Optional[str] = None

    # Video ingestion
    max_upload_size_mb: int = 500
    signed_url_ttl_seconds: int = 900  # 15 minutes

    model_config = SettingsConfigDict(
        env_file=Path(__file__).resolve().parents[1] / ".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )


settings = Settings()
