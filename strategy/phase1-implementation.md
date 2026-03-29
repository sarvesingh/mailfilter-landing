# Phase 1 — Implementation Plan

## Decisions (Confirmed March 29, 2026)

- **Beta billing:** All 100 beta users get free pro access. Stripe deferred to post-beta.
- **Hosting:** Railway ($5/mo hobby plan)
- **Weekly digest email:** Yes, included in MVP. Use Resend (free tier).
- **Image storage:** Supabase Storage with strict privacy settings. Images are user mail — treat as PII.
- **Token encryption:** Google OAuth tokens encrypted at rest with Fernet. Key in env var.
- **Sender normalization:** Claude normalizes in prompt + sender_aliases table + fuzzy matching fallback.
- **Auth approach:** Supabase Auth for login flow, store Google tokens ourselves in users table. Request `access_type=offline` + `prompt=consent` for refresh token.

## Project Structure

```
app/
  pyproject.toml                  # uv project — all deps
  alembic.ini                     # DB migrations config
  alembic/
    versions/                     # migration scripts
    env.py
  app/
    __init__.py
    main.py                       # FastAPI app factory, lifespan, middleware
    config.py                     # pydantic-settings: env vars, Supabase URL, etc.
    database.py                   # async SQLAlchemy engine + session factory
    models.py                     # SQLAlchemy ORM models (all tables)
    schemas.py                    # Pydantic request/response schemas
    dependencies.py               # FastAPI deps: get_db, get_current_user
    auth/
      __init__.py
      router.py                   # /auth/* endpoints
      supabase_client.py          # Supabase Auth client wrapper
      google_tokens.py            # Store/refresh per-user Google OAuth tokens
    mail/
      __init__.py
      router.py                   # /mail/* endpoints
      gmail_reader.py             # PORTED from poc — parameterized per-user
      classifier.py               # PORTED from poc — minimal changes
      service.py                  # orchestration: fetch + classify + store
    optout/
      __init__.py
      router.py                   # /optout/* endpoints
      service.py                  # opt-out logic, channel dispatching
      channels/
        __init__.py
        dmachoice.py
        optoutprescreen.py
        catalogchoice.py
        direct_sender.py
    dashboard/
      __init__.py
      router.py                   # server-rendered HTML endpoints
    impact/
      __init__.py
      calculator.py               # environmental stats computation
    workers/
      __init__.py
      daily_fetch.py              # arq task: fetch + classify for all users
      optout_processor.py         # arq task: process queued opt-outs
      worker.py                   # arq WorkerSettings
    templates/
      base.html
      dashboard.html
      login.html
      mail_detail.html
      optout_tracker.html
      settings.html
    static/
      style.css
      app.js                      # minimal JS (modals, fetch calls)
```

## Database Schema

### users
| Column | Type | Notes |
|--------|------|-------|
| id | UUID PK | gen_random_uuid() |
| email | TEXT UNIQUE NOT NULL | Google account email |
| name | TEXT | Display name from Google |
| google_access_token | TEXT | Encrypted (Fernet) |
| google_refresh_token | TEXT | Encrypted (Fernet) |
| google_token_expires_at | TIMESTAMPTZ | |
| supabase_user_id | TEXT UNIQUE | |
| subscription_tier | TEXT DEFAULT 'pro' | All beta users get pro |
| invite_code | TEXT | Code used to sign up |
| is_active | BOOLEAN DEFAULT true | |
| last_fetch_at | TIMESTAMPTZ | |
| created_at | TIMESTAMPTZ DEFAULT now() | |
| updated_at | TIMESTAMPTZ DEFAULT now() | |

### invite_codes
| Column | Type | Notes |
|--------|------|-------|
| id | UUID PK | |
| code | TEXT UNIQUE NOT NULL | e.g. BETA-XXXX |
| max_uses | INTEGER DEFAULT 1 | |
| times_used | INTEGER DEFAULT 0 | |
| created_at | TIMESTAMPTZ | |

### mail_pieces
| Column | Type | Notes |
|--------|------|-------|
| id | UUID PK | |
| user_id | UUID FK -> users.id NOT NULL | |
| mail_date | DATE NOT NULL | |
| gmail_message_id | TEXT | For dedup |
| image_index | INTEGER | Position in digest |
| image_url | TEXT | Supabase Storage URL |
| sender | TEXT | Identified by classifier |
| mail_type | TEXT NOT NULL | One of VALID_MAIL_TYPES |
| is_junk | BOOLEAN NOT NULL | |
| confidence | FLOAT | 0.0 to 1.0 |
| classifier_notes | TEXT | |
| is_stoppable | BOOLEAN | |
| stoppable_reason | TEXT | |
| user_override | TEXT NULL | 'junk' or 'real' |
| created_at | TIMESTAMPTZ DEFAULT now() | |

Indexes: (user_id, mail_date), (user_id, sender), (user_id, is_junk)
Unique: (user_id, gmail_message_id, image_index)

### opt_out_requests
| Column | Type | Notes |
|--------|------|-------|
| id | UUID PK | |
| user_id | UUID FK -> users.id NOT NULL | |
| sender | TEXT NOT NULL | |
| channel | TEXT NOT NULL | dmachoice, optoutprescreen, catalogchoice, direct_sender |
| status | TEXT NOT NULL DEFAULT 'queued' | queued -> submitted -> pending -> confirmed / failed |
| submitted_at | TIMESTAMPTZ | |
| confirmed_at | TIMESTAMPTZ | |
| notes | TEXT | |
| created_at | TIMESTAMPTZ DEFAULT now() | |
| updated_at | TIMESTAMPTZ DEFAULT now() | |

Indexes: (user_id, status), (user_id, sender)

### sender_directory
| Column | Type | Notes |
|--------|------|-------|
| id | UUID PK | |
| sender_name | TEXT UNIQUE NOT NULL | Normalized name |
| sender_aliases | TEXT[] | Alternate names |
| is_stoppable | BOOLEAN NOT NULL | |
| opt_out_channels | TEXT[] | Which channels work |
| opt_out_url | TEXT | Direct opt-out URL |
| category | TEXT | |
| notes | TEXT | |

### daily_stats
| Column | Type | Notes |
|--------|------|-------|
| id | UUID PK | |
| user_id | UUID FK -> users.id | |
| date | DATE | |
| total_pieces | INTEGER | |
| junk_count | INTEGER | |
| real_count | INTEGER | |
| stoppable_count | INTEGER | |

Unique: (user_id, date)

## API Endpoints

### Auth (/auth)
- GET /auth/login — login page with invite code + Google sign-in
- GET /auth/callback — OAuth callback, store tokens, set session, redirect to /dashboard
- POST /auth/logout — clear session, redirect to /
- GET /auth/validate-invite?code=BETA-XXXX — returns {valid: bool}

### Dashboard (server-rendered HTML)
- GET /dashboard — today's mail, stats, recent history
- GET /dashboard/history — full history with date filter + pagination
- GET /dashboard/mail/{id} — single piece detail
- GET /dashboard/optouts — opt-out request tracker
- GET /dashboard/impact — environmental impact page
- GET /dashboard/settings — account settings

### Mail API (JSON)
- GET /api/mail/today — today's classified pieces + stats
- GET /api/mail/history?from=&to=&page=&filter= — paginated history
- GET /api/mail/{id} — single piece detail
- PATCH /api/mail/{id} — user correction {user_override: "junk"|"real"}
- POST /api/mail/fetch-now — manual trigger, kicks off background job

### Opt-Out API (JSON)
- POST /api/optout/request — {sender: str} or {mail_piece_id: uuid}
- POST /api/optout/bulk — {sender_names: [str]}
- GET /api/optout/requests?status= — list with status filter
- GET /api/optout/requests/{id} — single request detail

### Stats API (JSON)
- GET /api/stats/summary — totals, top senders, impact numbers
- GET /api/stats/weekly — weekly breakdown for charts

## Background Jobs (arq)

1. **daily_fetch_all_users** — cron 5 PM ET. Fetch + classify for all active users.
2. **fetch_single_user** — on-demand via "Fetch Now" button or first login.
3. **process_opt_out_queue** — cron every 30 min. Process queued opt-outs.
4. **compute_daily_stats** — runs after daily fetch.
5. **send_weekly_digest** — cron Monday 9 AM. Weekly summary email via Resend.
6. **cleanup_expired_tokens** — weekly. Mark users with bad tokens as inactive.

## Sprint Plan

| Sprint | What | Days | Depends On |
|--------|------|------|------------|
| 0 | Scaffolding — FastAPI, Supabase, Alembic, Railway config | 2-3 | — |
| 1 | Auth — Google OAuth, sessions, invite codes | 3-4 | Sprint 0 |
| 2 | Mail fetch + classify — port POC, per-user creds, store in Postgres | 3-4 | Sprint 1 |
| 3 | Dashboard — today's mail, history, detail, corrections | 3-4 | Sprint 2 |
| 4 | Stats + impact calculator | 2 | Sprint 2 |
| 5 | Opt-out system — sender directory, queue, channel handlers | 4-5 | Sprint 2 |
| 6 | Daily automation, weekly digest email, polish | 3-4 | Sprints 3-5 |
| 7 | Production deploy, beta prep, invite codes | 2-3 | Sprint 6 |

Sprints 3, 4, 5 can run in parallel after Sprint 2.

**Total: ~5-6 weeks solo, 3-4 weeks with parallelization.**
