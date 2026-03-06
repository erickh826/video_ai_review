# Workflow 01: Bootstrap & Environment (POC)

## Goal
Get the project running locally with minimal secrets management using `.env` (POC only).

## Inputs
- Azure OpenAI credentials (already available)
- AWS S3 credentials (already available)
- Decide DB + Redis provider

## Recommendations
- Database: managed PostgreSQL (RDS Postgres or Azure Postgres Flexible Server)
- Redis: managed Redis (ElastiCache or Azure Cache for Redis)

Rationale:
- Long-running jobs (transcode, STT, LLM report) benefit from reliable queues + state.
- PostgreSQL supports future pgvector for RAG without new vendor.

## Tasks
1. Create `.env` from `.env.example` (never commit)
2. Ensure `.gitignore` contains:
   - `.env`
   - `.env.*`
3. Provision:
   - PostgreSQL instance
   - Redis instance
4. Verify connectivity from local dev machine:
   - `DATABASE_URL` works (SSL settings if required)
   - `REDIS_URL` works
5. Smoke test:
   - Start backend API
   - Hit `/health` endpoint (to be implemented)
   - Confirm it can read env values (without printing secrets)

## Acceptance Criteria
- App starts without throwing env errors
- DB and Redis connections succeed
- No secrets appear in logs