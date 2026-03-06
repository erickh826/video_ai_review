# Workflow 04: Review Generation (Rubric + Technique Plan) & Chat

## Goal
Generate a structured coaching report (grading secondary) and provide a chat endpoint that cites evidence.

## Inputs
- `rubric` JSON
- `technique_plan` JSON (auto by mode, with manual override support)
- `evidence_pack` JSON
- Azure OpenAI chat deployment

## Tasks
1. Determine mode:
   - `consulting_to_camera` (default)
   - `classroom` (if teacher marks it or model heuristics)
2. Build technique plan:
   - Use default weights by mode
   - Apply teacher override if provided
3. Call LLM to generate report:
   - System prompt: `prompts/review_report_system_prompt.txt`
   - User prompt template: `prompts/review_report_user_prompt_template.txt`
   - Must output JSON matching `schemas/review_output.schema.json`
4. Store output in DB and cache summary fields for UI
5. Chat endpoint:
   - `POST /api/videos/{video_id}/chat`
   - Retrieve transcript + evidence + report
   - Answer must cite timecodes and quote transcript snippets

## Acceptance Criteria
- Every dimension feedback item includes at least one evidence citation
- For each major issue, at least 2 zh-HK rewrites are produced
- Output validates against schema
- Chat answers can deep-link to the video timecode in UI