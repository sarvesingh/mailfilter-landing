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

## Project Overview

MailFilter is a product that helps people stop physical junk mail. This repo contains two things:

1. **Landing page** (`index.html`) — a static single-page marketing site deployed to GitHub Pages via `.github/workflows/pages.yml` on push to `main`.
2. **POC pipeline** (`poc/`) — a Python automation that reads USPS Informed Delivery emails, classifies mail images as junk/real using Claude's vision API, and logs results to Google Sheets.

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

`com.mailfilter.poc.plist` is a macOS launchd job that runs the pipeline daily at 5 PM. Load with `launchctl load com.mailfilter.poc.plist`.

### Architecture

The pipeline follows a linear flow: **fetch → classify → log**.

- `src/config.py` — env vars, paths, Google OAuth credential loading
- `src/gmail_reader.py` — queries Gmail API for Informed Delivery digest, extracts mail-scan images (skips images < 5 KB)
- `src/classifier.py` — sends each image to Claude vision API, parses JSON classification response. Mail types defined in `VALID_MAIL_TYPES` set.
- `src/sheets_logger.py` — appends classification rows to a Google Sheet via gspread, with per-date dedup
- `src/main.py` — orchestrator that wires the above together

Key dependencies: `anthropic`, `google-api-python-client`, `google-auth-oauthlib`, `gspread`, `python-dotenv`. Python 3.11.
