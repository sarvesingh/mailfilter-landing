# SnailSense - Business Plan

## Executive Summary

SnailSense is a consumer service that uses AI to help people identify and eliminate physical junk mail. Users classify their incoming mail through a smart camera app or by forwarding USPS Informed Delivery email digests. The service then automates opt-out requests on their behalf, progressively reducing the volume of junk mail they receive. Think of it as an **"unsubscribe button for physical mail."**

---

## Problem Statement

- Americans receive approximately **80 billion pieces of junk mail per year**
- The average household gets **40+ pounds of junk mail annually**
- Junk mail wastes time, clutters homes, and generates massive paper waste
- Opting out is fragmented and painful - dozens of different websites, forms, phone calls, and waiting periods across DMAchoice, CatalogChoice, OptOutPrescreen, and individual mailer opt-out processes
- No single solution exists to consolidate and automate the opt-out process

---

## Solution

A mobile-first service with two input channels and an automated opt-out engine:

### Input Channel 1: Smart Snap (Active)
- User points their phone camera at incoming mail
- App uses edge detection to auto-identify and auto-capture each mail piece
- Continuous scan mode allows flipping through a mail stack with automatic capture
- AI classifies each piece in real-time as junk or legitimate
- User confirms or corrects classification, training the model over time

### Input Channel 2: Informed Delivery Digest (Passive)
- One-time setup: user auto-forwards their daily USPS Informed Delivery email to a dedicated SnailSense address (e.g., `username@snailsense.com`)
- Service automatically parses grayscale mail images from the digest
- User receives a pre-classified summary before mail even arrives physically
- "Set it and forget it" experience

### Opt-Out Engine (Action)
- Each piece of mail confirmed as junk triggers automated opt-out actions:
  - Files removal requests with **DMAchoice** (Direct Marketing Association)
  - Submits opt-outs via **CatalogChoice**
  - Registers with **OptOutPrescreen.com** for pre-approved credit/insurance offers
  - Contacts individual mailers directly through their opt-out channels
  - Leverages state-level junk mail regulations where applicable
- Users can track opt-out status and see junk mail volume decrease over time

### Dual-Channel Advantage
- Informed Delivery provides a daily **preview** of incoming mail
- Smart Snap **fills gaps** that Informed Delivery misses (packages, local mail, magazines, flyers)
- Snap confirmations **train and improve** the AI model
- Together they provide comprehensive mail coverage

---

## Target Market

### Primary: Residential Consumers
- Homeowners and renters frustrated by junk mail
- Environmentally conscious consumers
- Busy professionals who value time savings
- Estimated addressable market: 130M+ US households

### Secondary: Small Businesses
- Offices receiving high volumes of unsolicited mail
- Property managers handling mail for multiple units
- Co-working spaces and shared offices

### Early Adopters
- Tech-savvy, environmentally conscious millennials and Gen Z homeowners
- Existing USPS Informed Delivery users (~50M+ registered users)
- Subscribers to sustainability-focused services

---

## Business Model & Revenue

### Subscription Tiers

| Tier | Price | Features |
|------|-------|----------|
| **Free** | $0/mo | Smart Snap classification (limited scans/month), basic junk mail stats |
| **Standard** | $4.99/mo | Unlimited scans, Informed Delivery integration, automated opt-outs (up to 20/month), junk mail tracking dashboard |
| **Premium** | $9.99/mo | Everything in Standard + unlimited opt-outs, priority processing, household/multi-user support, annual junk mail impact report |

### Additional Revenue Opportunities
- **Aggregated data insights** (anonymized) sold to market research firms
- **Sustainability partnerships** with environmental organizations
- **B2B API** for property management companies and mailroom services
- **White-label solution** for apartment complexes and HOAs

---

## Technology Stack

### Mobile App
- Cross-platform (iOS & Android)
- Camera module with real-time edge detection and auto-capture
- Local ML model for quick on-device pre-classification
- Push notifications for daily mail summaries

### Backend
- Cloud-based AI/ML pipeline for mail classification
  - OCR (Optical Character Recognition) to extract text from mail images
  - Image classification model trained on junk vs. legitimate mail
  - NLP to identify sender, mail type, and opt-out pathways
- Email ingestion service for Informed Delivery digest parsing
- Opt-out automation engine (web scraping, API integrations, form submissions)
- User dashboard and analytics

### AI/ML Approach
- Initial model trained on labeled junk mail datasets
- Continuous learning from user confirmations/corrections
- Classification categories: credit offers, catalogs, political mail, nonprofit solicitations, coupons/flyers, local business ads, legitimate mail
- Network effect: more users = better classification accuracy

---

## Competitive Landscape

| Competitor | What They Do | Gap We Fill |
|-----------|-------------|-------------|
| **PaperKarma** | App to photograph and unsubscribe from junk mail | Limited automation, declining support, no Informed Delivery integration |
| **DMAchoice** | Opt-out registry for direct mail | Manual process, only covers DMA members |
| **CatalogChoice** | Opt-out from catalogs | Narrow scope (catalogs only), manual |
| **USPS Informed Delivery** | Daily mail preview images | No classification, no opt-out capability |
| **Earth Class Mail** | Mail scanning & forwarding | Expensive, designed for remote workers not junk filtering |

**Our differentiation:**
- Dual input channels (Smart Snap + Informed Delivery)
- AI-powered classification that improves over time
- Consolidated, automated opt-out engine across multiple registries
- Measurable results (junk volume tracking)
- Consumer-friendly pricing

---

## Legal Considerations

- **Mail handling**: We never physically touch or intercept mail - we only process images. This avoids federal mail tampering regulations (18 U.S.C. 1708)
- **Privacy**: Mail images contain personal information (names, addresses). Must comply with state privacy laws (CCPA, etc.) and implement strong data encryption and retention policies
- **Opt-out authority**: Users explicitly authorize us to submit opt-out requests on their behalf. Clear Terms of Service and consent flows required
- **USPS Informed Delivery ToS**: Forwarding email digests is user-initiated. We do not access USPS systems directly or scrape their platform
- **CAN-SPAM / junk mail laws**: Physical mail is not covered by CAN-SPAM (email only), but various state laws provide opt-out rights we can leverage

---

## Go-to-Market Strategy

### Phase 1: MVP & Validation (Months 1-6)
- Launch Smart Snap app with basic AI classification
- Manual opt-out processing (semi-automated) to validate demand
- Target early adopters through sustainability communities, Reddit (r/zerowaste, r/declutter), and environmental blogs
- Free tier to drive downloads, gather training data

### Phase 2: Automation & Growth (Months 6-12)
- Add Informed Delivery email integration
- Fully automate opt-out engine
- Launch Standard and Premium subscription tiers
- Influencer partnerships (sustainability, home organization creators)
- PR push around environmental impact metrics

### Phase 3: Scale & Expand (Months 12-24)
- B2B offering for property managers and mailrooms
- Expand classification to support non-English mail
- Explore partnerships with recycling services
- Consider international expansion (Canada Post, Royal Mail, etc.)

---

## Key Metrics

- **Downloads & registrations**
- **Daily/weekly active users**
- **Mail pieces scanned per user**
- **Junk mail correctly classified (accuracy rate)**
- **Opt-out requests submitted**
- **Measurable junk mail reduction per user over time**
- **Free-to-paid conversion rate**
- **Monthly recurring revenue (MRR)**
- **Churn rate**

---

## Risks & Mitigations

| Risk | Mitigation |
|------|-----------|
| AI misclassifies legitimate mail as junk | User confirmation step before any opt-out action; easy "undo" flow |
| Opt-out requests ignored by mailers | Track success rates per mailer; escalate through regulatory channels; transparency with users |
| USPS changes Informed Delivery email format | Smart Snap as fallback channel; monitor for changes and adapt parser |
| Low user retention after junk decreases | Ongoing value through new mailer detection; expand into package tracking, mail organization |
| Privacy concerns with mail images | End-to-end encryption; minimal data retention; SOC 2 compliance; transparent privacy policy |
| Competitor launches similar feature | Speed to market, network effects from aggregated data, superior UX |

---

## Financial Projections (Year 1-3 Estimates)

| | Year 1 | Year 2 | Year 3 |
|--|--------|--------|--------|
| **Users (total)** | 50,000 | 250,000 | 1,000,000 |
| **Paid subscribers** | 5,000 (10%) | 37,500 (15%) | 200,000 (20%) |
| **Avg revenue/paid user/mo** | $6.50 | $7.00 | $7.50 |
| **Annual revenue** | $390K | $3.15M | $18M |
| **Key costs** | Dev team, cloud infra, opt-out processing | + Marketing, scaling infra | + B2B sales, international |

*Projections are illustrative and should be refined with market research.*

---

## Next Steps

1. **Validate demand** - Landing page with waitlist to gauge interest
2. **Build MVP** - Smart Snap app with basic classification (no opt-out automation yet)
3. **Gather training data** - Early users label their mail to build the classification model
4. **Test opt-out workflows** - Manually process opt-outs for beta users to understand success rates
5. **Iterate on the business plan** based on learnings

---

*Document version: 1.0 | Created: February 2026 | Status: Draft - For iteration*
