---
name: video-processing-pipeline
description: Design video frame extraction, batching, and AI inference pipeline for FastAPI systems.
keywords: ffmpeg, frame extraction, batching, async processing, ai pipeline
---

# Video Processing Pipeline

## Recommended Flow

1. Upload video
2. Save to disk
3. Extract frames (ffmpeg)
4. Batch frames
5. Send to AI model
6. Aggregate results
7. Store summary

---

# Frame Extraction Example

```python
import subprocess

def extract_frames(video_path: str, output_dir: str):
    command = [
        "ffmpeg",
        "-i", video_path,
        "-vf", "fps=1",
        f"{output_dir}/frame_%04d.jpg"
    ]
    subprocess.run(command)
```

# Batching Pattern
Never send 1000 frames at once.
```python
def batch_frames(frames, batch_size=10):
    for i in range(0, len(frames), batch_size):
        yield frames[i:i + batch_size]
```
# AI Aggregation Pattern
```python
async def analyze_video(frames):
    results = []
    for batch in batch_frames(frames):
        result = await ai_service.analyze(batch)
        results.append(result)

    return aggregate(results)
```

