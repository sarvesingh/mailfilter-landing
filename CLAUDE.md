# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Working Model

Claude operates as **Team Lead** for this project. The user (Sarve) is the product owner/founder.

**How it works:**
- Sarve gives direction and makes product decisions
- Claude is the single point of contact — takes requests, validates requirements, maintains the backlog, and owns quality
- Claude delegates to specialized agents as needed, reviews all output before presenting it

**Team roles (spawned as agents):**

| Role | Responsibility |
|------|---------------|
| **Engineering** | Code implementation — frontend, backend, infra |
| **Market Research** | Competitive analysis, user insights, market data |
| **Designer** | UX/UI decisions, layout, visual direction |
| **QA/Tester** | Validation, edge cases, code review |

Claude is not just a pass-through — validate before delegating, review before delivering. Push back on scope or quality issues. The user should never have to manage agents directly.

## Strategy Documents

- `strategy/phases.md` — Phased roadmap with customer profiles, pitches, tech stack, and key decisions
- `strategy/phase1-implementation.md` — Detailed sprint plan, DB schema, API endpoints, background jobs
- `strategy/market-research.md` — Competitive landscape, market data, viability assessment
- `snailsense-business-plan.md` — Original business plan (Feb 2026)

## Current Progress (as of March 29, 2026)

**Sprint 0 (Scaffolding):** Done. FastAPI app, SQLAlchemy models, Alembic migration, project structure.
**Sprint 1 (Auth):** Done. Google OAuth flow, session cookies, invite codes, login page.
**Sprint 2 (Mail Fetch + Classification):** Next. Port POC pipeline to multi-user production code.

Sprint 2 scope — create `app/app/mail/` module:
- `gmail_reader.py` — port from `poc/src/gmail_reader.py`, use per-user Google credentials from `app/app/auth/google_tokens.py`
- `classifier.py` — port from `poc/src/classifier.py`, minimal changes
- `service.py` — orchestrator: fetch Informed Delivery → classify images → store MailPiece rows in Postgres → upload images to Supabase Storage → update DailyStat
- `router.py` — `/api/mail/*` endpoints (today, history, detail, correction, fetch-now)
- Background job: `workers/daily_fetch.py` using arq

After Sprint 2, Sprints 3 (Dashboard), 4 (Stats), 5 (Opt-outs) can run in parallel.

## Project Overview

SnailSense is a product that helps people stop physical junk mail. This repo contains three things:

1. **Landing page** (`index.html`) — a static single-page marketing site deployed to GitHub Pages via `.github/workflows/pages.yml` on push to `main`.
2. **Web app** (`app/`) — FastAPI backend with Google OAuth, PostgreSQL via Supabase, Claude AI classification. In active development (Phase 1 MVP).
3. **POC pipeline** (`poc/`) — the original Python automation that reads USPS Informed Delivery emails, classifies mail images as junk/real using Claude's vision API, and logs results to Google Sheets. Being ported into the web app.

## Web App (app/)

### Setup

```bash
cd app
uv sync                                    # install dependencies
cp .env.example .env                       # fill in all required vars (see config.py)
alembic upgrade head                       # run migrations
uvicorn app.main:app --reload              # start dev server at localhost:8000
```

### Key Architecture

- **Auth flow:** Google OAuth with `gmail.readonly` scope → encrypted token storage (Fernet) → signed session cookies (itsdangerous, 30-day expiry)
- **Token management:** `app/auth/google_tokens.py` — encrypt/decrypt tokens, auto-refresh expired credentials, persist back to DB
- **Dependencies:** `app/dependencies.py` — `get_current_user` (401 if unauthenticated), `get_current_user_optional` (returns None)
- **Models:** `app/models.py` — User, InviteCode, MailPiece, OptOutRequest, SenderDirectory, DailyStat
- **All blocking Google API calls** use `asyncio.run_in_executor` to avoid blocking the event loop

### Porting from POC

The POC `classifier.py` and `gmail_reader.py` are directly reusable. Key changes needed:
- Replace single-user config with per-user Google credentials from the DB
- Replace Google Sheets logging with Postgres (MailPiece model)
- Add Supabase Storage for mail images
- Make async (POC is synchronous)

## Landing Page

Pure HTML/CSS, no build step. Open `index.html` in a browser to preview. Deployed automatically to GitHub Pages on push to `main`.

## POC Pipeline

### Setup

```bash
cd poc
uv sync                                    # install dependencies into .venv
cp .env.example .env                       # fill in ANTHROPIC_API_KEY, GOOGLE_SHEET_ID
# Place credentials.json from Google Cloud Console in poc/
uv run python scripts/setup_auth.py        # one-time OAuth consent → creates token.json
```

### Running

```bash
cd poc
uv run python -m src.main                  # process today's mail
uv run python -m src.main 2026-03-28       # process a specific date
```

### Scheduled Execution

`com.snailsense.poc.plist` is a macOS launchd job that runs the pipeline daily at 5 PM. Load with `launchctl load com.snailsense.poc.plist`.

### Architecture

The pipeline follows a linear flow: **fetch → classify → log**.

- `src/config.py` — env vars, paths, Google OAuth credential loading
- `src/gmail_reader.py` — queries Gmail API for Informed Delivery digest, extracts mail-scan images (skips images < 5 KB)
- `src/classifier.py` — sends each image to Claude vision API, parses JSON classification response. Mail types defined in `VALID_MAIL_TYPES` set.
- `src/sheets_logger.py` — appends classification rows to a Google Sheet via gspread, with per-date dedup
- `src/main.py` — orchestrator that wires the above together

Key dependencies: `anthropic`, `google-api-python-client`, `google-auth-oauthlib`, `gspread`, `python-dotenv`. Python 3.11.
