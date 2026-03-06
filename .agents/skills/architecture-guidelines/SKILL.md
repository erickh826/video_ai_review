---
name: architecture-guidelines
description: Architecture guidance for building AI video review proof-of-concept systems using FastAPI.
---

# POC Architecture Guidelines

## POC Goals

- Validate idea
- Keep it simple
- Avoid overengineering
- Ship fast

---

## Recommended Stack

- FastAPI
- SQLite or Postgres
- Local file storage
- FFmpeg
- OpenAI / Vision model
- BackgroundTasks (or Celery if needed)

---

## Scale Later Strategy

Phase 1:
- Single service
- BackgroundTasks

Phase 2:
- Move to Celery
- Add Redis
- Add object storage (S3)

Phase 3:
- Microservices