# Workflow 03: Transcription (No GPU) & Evidence Pack

## Goal
Generate zh-HK transcript with timestamps using cloud STT (since no GPU),
then produce an `evidence_pack` JSON that is deterministic and cheap.

## Inputs
- Video audio track (extracted with FFmpeg)
- STT provider (recommended: Azure AI Speech)

## Tasks
1. Extract audio:
   - Store: `S3_PREFIX/{video_id}/audio/audio.wav` (or .m4a)
2. Call STT:
   - Return transcript segments with timecodes
   - Preserve colloquial particles; do not normalize away fillers in quoted text
3. Create evidence detections:
   - filler words list (zh-HK): 「即係」「咁」「其實」「然後」...
   - closed questions patterns: 「你明唔明」「係咪」「可唔可以」...
   - harsh negation patterns: 「唔得」「唔好」「你錯咗」...
   - open question heuristics: 「點睇」「可唔可以講多啲」...
4. Compute metrics:
   - words_per_minute
   - silence_ratio (optional if audio analysis available)
   - question_ratio

## Outputs
- `transcript.json` (segments with start_sec/end_sec)
- `evidence_pack.json` matching schema:
  - `schemas/evidence_pack.schema.json`

## Acceptance Criteria
- Transcript segments have valid time ranges and are in zh-HK Traditional
- Evidence pack validates against schema
- Detections include timecoded evidence and references to segments