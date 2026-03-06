---
name: fastapi-ai-video-patterns
description: Build FastAPI endpoints for AI-powered video analysis systems. Use for file upload, async processing, background tasks, inference orchestration, and response modeling.
keywords: fastapi, video upload, background tasks, async, ai inference, streaming, file handling
---

# FastAPI AI Video Patterns

## Purpose

Design clean FastAPI APIs for:
- Video upload
- AI model processing
- Background inference
- Status tracking
- Result retrieval

Use this skill when building:
- AI video review APIs
- Media processing services
- ML inference endpoints

---

# Core Architecture Pattern (POC-Friendly)

Recommended structure:
app/
main.py
api/
routes/
video.py
services/
video_service.py
ai_service.py
schemas/
video.py
core/
config.py
workers/

---

# ✅ File Upload Endpoint Pattern

```python
from fastapi import APIRouter, UploadFile, File, BackgroundTasks
from app.services.video_service import process_video

router = APIRouter()

@router.post("/videos")
async def upload_video(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...)
):
    video_id = await save_video(file)

    background_tasks.add_task(
        process_video,
        video_id
    )

    return {"video_id": video_id, "status": "processing"}
```

# ✅ Background Processing Pattern
Never block request threads with heavy AI work.

```python
async def process_video(video_id: str):
    frames = extract_frames(video_id)
    result = await ai_service.analyze(frames)
    save_result(video_id, result)
```

# ✅ Status Polling Pattern
```python
@router.get("/videos/{video_id}")
async def get_status(video_id: str):
    return video_service.get_status(video_id)

Response model example:
class VideoStatusResponse(BaseModel):
    video_id: str
    status: str  # processing | completed | failed
    result: Optional[dict] = None
```

#✅ AI Service Isolation Pattern
Keep AI logic separate:
```python
class AIService:
    async def analyze(self, frames):
        # call OpenAI / local model / vision model
        ...
```
Never mix:

Routing
Business logic
AI inference
File IO

# ✅ Large File Handling Rules
Use UploadFile, not bytes
Stream to disk
Do not keep full video in memory
Store file path, not raw file

# ✅ POC Best Practices
Use SQLite or simple Postgres
Store status in DB
Add logging
Add request IDs
Keep it simple

# ❌ Avoid in POC
Premature microservices
Kubernetes complexity
Over-engineered abstraction

---




