# MailFilter — Phased Strategy

## Master Pitch

**"Stop junk mail before it hits your mailbox — automatically."**

---

## Phase 1 — "See the Problem" (Weeks 1-8): MVP

**Pitch:** "Finally see how much of your mail is garbage — and start killing it."

**Customer:** Eco-conscious early adopters. Tech-savvy, already on Informed Delivery, hangs out on Reddit/HN. Tried PaperKarma, hated the manual effort.

**What we build:**
- Web app with Google OAuth signup
- Auto-fetch Informed Delivery daily, classify with Claude, store in Postgres
- Dashboard: today's mail, history, junk/real breakdown, sender identification
- "Stoppable" vs "unstoppable" labels per piece
- One-click "opt me out" → queues requests
- Semi-automated opt-outs (top 20 senders, DMAchoice, OptOutPrescreen, CatalogChoice)
- Opt-out status tracker
- Basic environmental impact counter
- Invite-only (100 beta users)

**Revenue:** Free classification + $4.99/mo or $39.99/yr for opt-outs

**Acquisition:** Reddit (r/zerowaste, r/declutter), Show HN, niche newsletters, Informed Delivery Facebook groups

**Conversion trigger:** First weekly email — "18 pieces classified. 14 were junk. Opt out of 11 with one click."

---

## Phase 2 — "Fix the Problem" (Months 3-5): Retention + Automation

**Pitch:** "Watch your junk mail disappear, week by week."

**Customer:** Pragmatic homeowners. Sorts mail nightly, shreds credit offers, has googled "how to stop junk mail." Cares about results, not dashboards.

**What we build:**
- Expanded automated opt-outs across long tail of senders
- Weekly digest emails, milestone notifications ("Spectrum stopped mailing you!")
- Junk Mail Score (gamified progress tracking)
- User classification corrections (training data)
- Outlook/Microsoft email support
- Free-to-paid conversion funnel, annual plan push

**Revenue:** Free→paid conversion at scale

**Acquisition:** SEO ("how to stop junk mail" — 40K+ monthly searches), Nextdoor, YouTube declutter creators, testimonials from Phase 1 users

**Conversion trigger:** 30-day free trial progress email with personalized stats and social proof.

---

## Phase 3 — "Complete Coverage" (Months 6-9): Smart Snap + Mobile

**Pitch:** "Every piece of junk mail, caught — whether USPS sees it or not."

**Customer:** Household managers. Working parents managing mail for the whole family. Frustrated that Informed Delivery misses some mail and can't handle multiple people.

**What we build:**
- PWA with camera for Smart Snap (catches what Informed Delivery misses)
- Household support (multiple people at same address)
- Shareable environmental impact cards
- Referral program (free month per referral)
- Classification model fine-tuned on real user data

**Revenue:** Household tier $7.99/mo

**Acquisition:** Facebook mom/neighborhood groups, Instagram Reels/TikTok, referral program, local press

**Conversion trigger:** First Smart Snap that works — photograph a mailer, AI classifies it, opt-out submitted instantly.

---

## Phase 4 — "Platform" (Months 10-15): Scale + B2B

**Pitch:** "The infrastructure layer for a world with less junk mail."

**Customers:**
- Property managers (340+ units, mail room overhead problem)
- Environmental nonprofits (need data for Do Not Mail registry advocacy)

**What we build:**
- API for property managers and mailrooms
- Anonymized, aggregated junk mail trend data
- Environmental org partnerships
- "State of Junk Mail in America" data report
- Do Not Mail registry advocacy using aggregated user data

**Revenue:** B2B API contracts + partnerships

**Acquisition:** BiggerPockets, NARPM conferences, AppFolio/Buildium integrations, direct outreach to NRDC/Sierra Club, press with data angle

**Conversion trigger:** For PMs — demo showing labor savings in $/unit/month. For nonprofits — first data report with campaign-ready stats.

---

## Production Tech Stack

| Layer | Choice |
|-------|--------|
| Backend | Python + FastAPI |
| Database | PostgreSQL via Supabase |
| Auth | Google OAuth (double duty — Gmail access + login) |
| Frontend | Server-rendered HTML + minimal JS (MVP), React dashboard later |
| Hosting | Railway or Fly.io ($5-10/mo) |
| Task queue | arq (lightweight async jobs) |
| Mobile (Phase 3) | PWA / Expo |
| **Estimated MVP cost** | **Under $50/month** |

---

## Key Strategic Decisions

1. **Launch with Informed Delivery via Gmail OAuth** — not Smart Snap, not email forwarding. Passive, one-click, POC already works.
2. **Transparency is the moat** — show what can/can't be stopped. "Reduces 50-70% in 8-12 weeks." Not "eliminate."
3. **Free to see the problem, pay to fix it** — free classification, paid opt-outs. No per-opt-out limits.
4. **Semi-automated opt-outs first** — manual fulfillment for first 50 users, then automate top 3 channels, then long tail.
5. **Annual pricing push** — monthly invites churn before results arrive.
6. **Web-first, no mobile app until Phase 3.**
