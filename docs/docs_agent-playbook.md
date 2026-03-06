# Agent Playbook (video_review POC)

This repo builds a **video review chatbot** that generates **timecoded, evidence-based coaching feedback** (grading is secondary) for consulting/teaching videos in **zh-HK** with colloquial language preserved.

## Goals (POC)
- Upload a video (<= 10 min typical)
- Generate:
  - transcript with timestamps (keep colloquial zh-HK)
  - evidence pack (detections + metrics)
  - review report JSON (aligned to rubric + technique plan)
- Provide a teacher-facing UI / API to:
  - read a structured report
  - ask a chatbot question that cites evidence/timecodes

## Non-goals (POC)
- No on-device or self-hosted GPU inference
- No “diagnosis”, “therapy claims”, or promises of outcomes
- No facial identity recognition
- No training on customer videos (vendor settings must be configured accordingly)

---

## Operating Principles (how agents should work)
### 1) Evidence-first, then narrative
Agents must never “free-write” feedback without:
- transcript segment(s) with timecodes
- detection(s) / metric(s) supporting the claim

### 2) Structured outputs everywhere
All AI outputs should be validated against JSON schemas under `/schemas`:
- `evidence_pack.schema.json`
- `review_output.schema.json`
- plus rubric + technique plan schemas

### 3) Locale & tone constraints (zh-HK)
- Output in Traditional Chinese (Hong Kong style)
- Preserve colloquial particles (e.g., 「咁」、「喎」、「即係」) when quoting originals
- Rewrites should be *professional but natural* zh-HK, not overly formal Mainland phrasing

### 4) Safety & privacy
- Do not infer student intent or inner states
- Do not diagnose or label
- No promises of therapeutic/learning outcomes
- Use signed URLs for video access; do not leak URLs/keys in logs
- Keys stored in `.env` for POC only (never commit); production uses Key Vault/Secrets Manager

---

## Agent Roles & How to Coordinate
See: `docs/roles.md`

When running work with an AI coding assistant (Copilot or other):
- Assign one role at a time to reduce conflicts
- For any change that affects schemas/prompts, update docs and add a small validation test (even a simple JSON schema validation script)

---

## Workflows (entry points)
See: `docs/workflows/`

Recommended execution order:
1. `01-bootstrap-and-env.md`
2. `02-video-ingestion-and-storage.md`
3. `03-transcription-and-evidence.md`
4. `04-review-generation-and-chat.md`

---

## Definition of Done (POC)
A single video can be processed end-to-end producing:
- transcript JSON with timestamps
- evidence_pack JSON (detections + metrics)
- review_output JSON with:
  - per-dimension feedback for the 8 dimensions
  - at least 2 zh-HK rewrite suggestions per major issue
  - timecoded evidence for every claim
- a chatbot endpoint that answers “why” questions with citations

---

## Suggested Tech Stack (implementation-friendly)
- Backend: Python + FastAPI
- Jobs: Celery + Redis
- DB: PostgreSQL
- Storage: AWS S3
- STT: Azure AI Speech (since no GPU)
- LLM: Azure OpenAI (chat + embeddings optional)
- Video processing: FFmpeg (HLS + thumbnails)

(If your implementation differs, update this section for accuracy.)