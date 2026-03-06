# Workflow 06: Security & Privacy (POC baseline, AWS+Azure hybrid)

## Goal
Establish a **minimum viable** security & privacy posture for the POC:
- Raw videos remain in **AWS S3**
- Only **audio** is sent to **Azure Speech** for transcription
- Only **text/evidence** is sent to **Azure OpenAI** for review generation / chat
- No secrets are committed, leaked in logs, or exposed in URLs

This is not a full compliance program; it is a practical baseline that avoids common mistakes.

---

## Data classification & handling rules (POC)
### Data types
1. **Raw video** (highest sensitivity)
2. **Audio track** (high sensitivity)
3. **Transcript** (high sensitivity)
4. **Evidence pack / metrics** (medium-high; still derived from sensitive data)
5. **Review report** (medium-high; may contain quoted transcript)
6. **Rubric / technique catalog / prompts** (low-medium; mostly internal IP)

### POC handling principles
- Keep (1) raw video in S3 only.
- Avoid sending raw video to any 3rd party service.
- If possible, avoid storing extracted audio long-term; treat it as a temporary artifact.
- Treat transcript and review as sensitive; require authenticated access.

---

## Cloud boundary design (AWS + Azure)
### What goes to Azure Speech (STT)
- **Audio only** (e.g., WAV/M4A), scoped to the minimal duration needed.
- Do not include:
  - raw video
  - S3 signed URLs
  - user IDs or personal identifiers in request metadata

### What goes to Azure OpenAI (LLM)
- Only:
  - transcript snippets required for evidence
  - evidence pack (structured, minimal)
  - rubric + technique plan
- Avoid:
  - full raw transcript if not needed for the task
  - any stable identifiers (student name, email, phone)
  - raw S3 URLs

---

## Secrets management (POC)
### Allowed for POC
- Use `.env` / `.env.local` on developer machines
- Use environment variables in runtime

### Not allowed (even in POC)
- Committing `.env` or keys to git
- Copy/pasting secrets into docs
- Printing keys in logs or error traces

### Required repo hygiene
- `.gitignore` MUST include:
  - `.env`
  - `.env.*`
- Provide `.env.example` only (no values)

---

## Access control
### API authentication (baseline)
- Require authentication for:
  - upload
  - transcript retrieval
  - review retrieval
  - chat endpoint
- Ensure per-video authorization checks:
  - a teacher can only access their class/cohort videos (as per your product rules)

### Signed URLs for S3 objects
- Use **short-lived** signed URLs:
  - raw video playback: short TTL (e.g., 5–15 minutes)
  - HLS segments: consider signing playlist and using CDN policies if needed
- Never store signed URLs in DB (store object keys only).

---

## Logging & observability rules
- Never log:
  - API keys
  - connection strings
  - signed URLs
  - raw transcript content by default
- If you must log AI payloads for debugging:
  - gate behind an explicit `APP_ENV=dev` + feature flag
  - redact/trim:
    - names/emails/phone numbers (basic patterns)
    - long transcript sections
- Prefer logging:
  - `video_id`
  - job stage (upload/transcode/stt/evidence/llm)
  - durations + status codes
  - token usage/cost metrics (without including raw content)

---

## Data retention (POC defaults)
Set a conservative default policy (tune later):
- Raw video in S3: 30–90 days (configurable per tenant)
- Extracted audio: delete after STT completion (recommended)
- Transcript + evidence + review report: 90 days (configurable)
- Allow manual delete:
  - per video delete should remove all derived artifacts

---

## Content safety / guardrails for feedback generation
The system must:
- Avoid diagnosis/labels (no mental health diagnoses)
- Avoid outcome promises (“guaranteed improvement”)
- Avoid mind-reading (“學生一定覺得你…”) — use probabilistic language:
  - “可能會令學生覺得…”
  - and always cite evidence/timecodes

The LLM output must:
- be validated against `schemas/review_output.schema.json`
- include timecoded evidence for every non-trivial claim
- include at least one actionable next step

---

## Checklist (Definition of Done for this workflow)
- [ ] `.env` is ignored by git; `.env.example` exists
- [ ] S3 access uses IAM credentials; no bucket is public
- [ ] Video access uses signed URLs with short TTL
- [ ] STT pipeline sends **audio only** to Azure Speech
- [ ] LLM pipeline sends **text/evidence only** to Azure OpenAI
- [ ] Logs are redacted and do not include secrets or signed URLs
- [ ] A retention plan exists and is documented (even if manual cleanup in POC)