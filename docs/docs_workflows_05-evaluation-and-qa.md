# Workflow 05: Evaluation & QA (POC)

## Goal
Create a lightweight but effective QA/evaluation process so the system is:
- **Evidence-grounded** (no ungrounded claims)
- **Useful to teachers** (clear, actionable)
- **Consistent zh-HK style** (colloquial preserved; rewrites natural)
- **Aligned to selected techniques** (MI/CBT/ACT/SFBT)

This workflow defines:
1) a small evaluation dataset (10–20 samples)
2) automated checks (schema + evidence rules)
3) human review checklist + scoring rubric for the POC

---

## Evaluation set (POC benchmark)
### Recommended size
- Start with **12 videos** (or transcripts if videos are sensitive/limited)
  - 8 consulting-to-camera
  - 4 classroom

If real videos are not available, use **simulated transcripts** that include:
- filler words (即係、咁、其實…)
- harsh negation examples (唔得、你錯咗…)
- closed questions (你明唔明、係咪…)
- places where MI/CBT/ACT/SFBT rewrites would differ

### What to store for each sample
- `video_id` (or `sample_id`)
- ground truth metadata:
  - mode: `consulting_to_camera | classroom`
  - expected top 2–3 issues (human-labeled)
- inputs:
  - transcript segments with timecodes (real or simulated)
- outputs to evaluate:
  - `evidence_pack.json`
  - `review_output.json`

> For POC, it’s acceptable to benchmark on transcripts only. The key is: **timecodes + evidence + rewrite quality**.

---

## Automated checks (must-pass gates)
These checks should run in CI or at least as a local script.

### A) JSON schema validation
- `evidence_pack` validates against `schemas/evidence_pack.schema.json`
- `review_output` validates against `schemas/review_output.schema.json`

### B) Evidence coverage
For every `dimension_feedback[*]` item in `review_output`:
- must include `evidence` array with >= 1 entry
- every evidence entry must contain:
  - `start_sec`, `end_sec` (numbers)
  - `transcript_quote` (non-empty string)

### C) Timecode sanity
- `0 <= start_sec < end_sec <= video_length_sec` (if length known)
- evidence quotes must match (or be a substring of) the transcript text within that time range
  - POC rule: “substring match” is OK (to tolerate punctuation differences)

### D) Rewrite requirements
For every issue that includes `suggested_rewrites_zh_hk`:
- must provide **>= 2** rewrites
- rewrites must be in Traditional Chinese (best-effort heuristic)
- rewrites must not include disallowed language:
  - diagnosis labels
  - therapy outcome promises
  - shaming / insulting words

### E) Technique adherence (best-effort)
If `techniques_used` is present for rewrites:
- must be drawn from known technique ids in `technique_catalog`
- if teacher locks a school (e.g., MI only), rewrites must not use other school technique ids

---

## Human review checklist (POC)
Each sample is reviewed by 1–2 humans (teacher/coach + product owner).

### Score each dimension (0–2)
0 = poor / not usable  
1 = acceptable  
2 = good  

**Criteria**
1) **Groundedness**: claims are supported by evidence/timecodes
2) **Actionability**: advice includes concrete next steps, not vague tips
3) **zh-HK naturalness**: rewrites sound like HK usage, not overly formal
4) **Tone**: supportive coach; avoids blaming
5) **Technique fit**: MI/CBT/ACT/SFBT suggestions make sense for the issue
6) **Teacher usefulness**: helps teacher spot issues quickly

### Pass threshold (POC)
- Automated checks: **100% pass**
- Human checklist: average >= **1.4/2** across criteria
- No “critical failures”:
  - diagnosis/labeling
  - ungrounded claims stated as facts
  - leaking sensitive data in output/logs

---

## Regression strategy (POC)
Whenever you change:
- prompts
- rubric definitions
- technique catalog entries
- evidence extraction rules

Run the benchmark set again and compare:
- number of evidence citations
- top issues list drift
- rewrite style drift (manual spot check)
- presence/absence of disallowed content

---

## Deliverables
- `docs/workflows/05-evaluation-and-qa.md` (this file)
- A folder for samples (suggested; optional for POC):
  - `eval_samples/`
    - `sample_001/transcript.json`
    - `sample_001/evidence_pack.json`
    - `sample_001/review_output.json`

---

## Acceptance Criteria
- A repeatable evaluation process exists (even if manual)
- Changes to prompts/rules trigger re-evaluation
- The system demonstrates:
  - evidence-grounded feedback
  - helpful zh-HK rewrites
  - technique-consistent suggestions