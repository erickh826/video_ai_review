# Workflow 02: Video Ingestion & Storage (S3 + SQS trigger)

## Goal
Enable client upload to S3 using presigned URLs, then automatically trigger processing via:
**S3 Event -> SQS -> Worker (ECS)**.

This decouples upload from processing and avoids running heavy work in the API.

---

## Architecture (POC)
Client
  -> (GET presigned PUT) API (ECS)
  -> (PUT object) S3 (raw upload)
  -> (ObjectCreated event) S3 Notification
  -> SQS queue
  -> Worker (ECS) polls SQS, processes jobs
  -> Writes outputs to S3 + DB

---

## Inputs
- S3 bucket: `video-review-ai-useast`
- S3 prefix layout:
  - `video-review/<video_id>/raw/original.mp4`
  - derived outputs under `audio/`, `thumbs/`, `hls/`, `ai/`

## Tasks
### 1) API: create upload session
- `POST /api/videos`
  - creates a `video_id`
  - persists DB record with status `awaiting_upload`
  - returns:
    - `video_id`
    - `presigned_put_url` for `raw/original.mp4`
    - optional `presigned_get_url` for playback

### 2) Client uploads raw video to S3
- Key must be:
  - `video-review/<video_id>/raw/original.mp4`

### 3) S3 bucket notification -> SQS
- Configure S3 event notifications for `ObjectCreated:*`
- Filter prefix:
  - `video-review/`
- Filter suffix:
  - `.mp4` (optional)
- Destination:
  - SQS queue `video-review-raw-uploads`

### 4) Worker polls SQS
Worker consumes SQS messages and derives:
- `bucket`
- `object_key`
- `video_id` (parse from key)

Worker then:
- downloads raw video from S3
- extracts audio with FFmpeg
- transcribes via Azure Speech
- generates evidence + review via Azure OpenAI
- uploads derived outputs to S3 under:
  - `audio/`, `thumbs/`, `hls/`, `ai/`
- updates DB status (processing -> done / failed)

---

## Acceptance Criteria
- Client can upload raw video via presigned PUT (no API streaming upload)
- Upload produces an SQS message
- Worker receives message and starts processing within expected time
- Outputs are written to S3 and DB status is updated