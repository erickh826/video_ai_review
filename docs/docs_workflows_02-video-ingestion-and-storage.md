# Workflow 02: Video Ingestion & Storage (S3)

## Goal
Allow uploading a video and storing it in S3, generating:
- video record in DB
- S3 object key
- thumbnail(s)
- HLS output (optional for POC but recommended)

## Inputs
- AWS S3 bucket + credentials
- FFmpeg available in runtime

## Tasks
1. API: `POST /api/videos`
   - Accept upload (multipart) or generate presigned upload URL
2. Store raw video to S3:
   - Key convention: `S3_PREFIX/{video_id}/raw/{filename}`
3. Persist DB record:
   - `video_id`, status, storage keys, created_at
4. Generate thumbnail:
   - `S3_PREFIX/{video_id}/thumbs/0001.jpg`
5. (Recommended) Generate HLS:
   - `S3_PREFIX/{video_id}/hls/*.m3u8` and segments

## Acceptance Criteria
- A video can be uploaded and played back via signed URL
- DB reflects correct object keys
- Thumbnail exists in S3
- Large files do not time out (use presigned upload if needed)