# Roles (video_review)

This project is designed to be built with assistance from AI agents. To avoid chaos, work is split into clear roles.

## 1) Product & Rubric Owner
**Responsibilities**
- Define rubric dimensions, definitions, examples, and scoring interpretation
- Decide teacher-facing UX: what outputs matter most
- Approve technique mixing policy defaults for:
  - consulting-to-camera
  - classroom

**Artifacts owned**
- `schemas/rubric.schema.json` (content & defaults)
- `schemas/technique_plan.schema.json` (policy)
- examples for zh-HK rewrite style

---

## 2) Prompt / Technique Engineer
**Responsibilities**
- Maintain prompts and technique catalog content
- Ensure outputs comply with JSON schema
- Ensure guardrails: no diagnosis, no promises, evidence-required

**Artifacts owned**
- `prompts/*`
- `schemas/technique_catalog.schema.json` (content)
- example rewrites library (future)

---

## 3) Backend / Pipeline Engineer
**Responsibilities**
- Video ingestion, storage, metadata
- Orchestration of:
  - FFmpeg transform
  - STT calls
  - evidence extraction
  - LLM report generation
- Job status and retries

**Artifacts owned**
- API endpoints
- queue workers
- storage adapters
- DB models/migrations

---

## 4) Frontend Engineer
**Responsibilities**
- Video player with markers
- Transcript viewer synced with video
- Report viewer
- Chat UI that links to timecodes

**Artifacts owned**
- UI components
- integration with backend APIs

---

## 5) QA / Evaluator
**Responsibilities**
- Define acceptance tests for:
  - timecode correctness
  - evidence citations
  - zh-HK rewrite quality
  - hallucination checks (claims must be grounded)
- Build a small benchmark set (10–20 sample videos or simulated transcripts)

**Artifacts owned**
- test cases
- evaluation checklist
- regression results