<p align="center">
  <img src="assets/banner.jpg" alt="GTM Command Center — Autonomous Growth Engine" width="100%">
</p>

<h1 align="center">GTM Engineering Command Center</h1>

<p align="center">
  <strong>The autonomous growth operating system for Claude Code.</strong><br>
  Multichannel orchestration. Andromeda-native. Neural pre-testing. Self-learning.<br>
  One north star: <em>print cash.</em>
</p>

<p align="center">
  <a href="#installation"><img src="https://img.shields.io/badge/Claude_Code-Plugin-7C3AED?style=for-the-badge&logo=data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZpZXdCb3g9IjAgMCAyNCAyNCI+PHBhdGggZD0iTTEyIDJDNi40OCAyIDIgNi40OCAyIDEyczQuNDggMTAgMTAgMTAgMTAtNC40OCAxMC0xMFMxNy41MiAyIDEyIDJ6IiBmaWxsPSJ3aGl0ZSIvPjwvc3ZnPg==&logoColor=white" alt="Claude Code Plugin"></a>
  <img src="https://img.shields.io/badge/version-1.3.0-C980FC?style=for-the-badge" alt="Version 1.3.0">
  <img src="https://img.shields.io/badge/license-MIT-FF7151?style=for-the-badge" alt="MIT License">
  <img src="https://img.shields.io/badge/channels-7-07070E?style=for-the-badge" alt="7 Channels">
</p>

<p align="center">
  <a href="#slash-commands">22 Commands</a> •
  <a href="#agents">15 Agents</a> •
  <a href="#skills">16 Skills</a> •
  <a href="#routines">4 Cloud Routines</a> •
  <a href="#knowledge-base">3 Knowledge Bases</a>
</p>

---

## What Is This?

The GTM Engineering Command Center transforms Claude Code into a **full-stack autonomous growth engine**. It doesn't just run ads — it owns the entire revenue lifecycle across every channel, powered by April 2026 operator-level knowledge from $100K-$500K/month spenders:

```
        ┌─────────────────────────────────────────────────────┐
        │              AARRR FUNNEL OWNERSHIP                 │
        │                                                     │
        │  Acquisition ──→ Activation ──→ Retention           │
        │  (Meta, Google,  (Onboarding,   (Email drips,      │
        │   TikTok, SEO,    Landing pages,  Engagement         │
        │   LinkedIn)       Emails)         loops)             │
        │                                                     │
        │  Revenue ──→ Referral                               │
        │  (Pricing,    (Viral loops,                         │
        │   Upsells,     Ambassador                           │
        │   Checkout)    programs)                             │
        └─────────────────────────────────────────────────────┘
                              │
                    ┌─────────┴─────────┐
                    │  DIAGNOSE → FIX   │
                    │  EMQ audit first. │
                    │  Then find where   │
                    │  revenue leaks.   │
                    └───────────────────┘
```

**It detects your stack.** Scans your codebase for 20+ integrations (Resend, PostHog, Stripe, Tailwind, Supabase, Vercel, Mux, Sentry, etc.) and adapts.

**It understands Andromeda.** Entity Clustering, ARM, Event Match Quality — the plugin knows how Meta's algorithm actually works in April 2026 and structures campaigns accordingly.

**It diagnoses bottlenecks.** Correlates data across PostHog, Stripe, Meta, Google, email, and SEO to find WHERE your funnel is broken. EMQ audit first — because bad data kills creative.

**It generates assets.** 20+ visually distinct creatives across 4 levers (Persona × Messaging × Hook × Format), landing pages using your design system, email drips matching your template style, SEO content.

**It pre-tests with neuroscience.** Tribe v2 brain prediction scores every creative before deployment. Dead Zone Editing cuts the boring parts. Only winners get budget.

**It verifies its own work.** Playwright, Computer Use, and Chrome DevTools QA every deployment — pixel fires, EMQ checks, mobile responsiveness, funnel walkthroughs.

**It never sleeps.** Cloud Routines pull metrics daily, optimize weekly, and check every PR for conversion tracking completeness.

---

## The Five Laws (from the Media Buying Atlas)

> These laws govern every decision the plugin makes.

| Law | Principle |
|-----|-----------|
| **1. Creative Is the Targeting** | Andromeda's Entity Clustering groups similar ads into one ticket. You need 50-200 visually distinct Entity IDs per week. Minor text variations are dead. |
| **2. Data Hygiene Is the Moat** | ARM reads your conversion data BEFORE your creative. EMQ 8-10 unlocks the full model. You cannot out-creative bad data. |
| **3. Consolidation Beats Fragmentation** | One campaign, 1-2 ad sets, 20-50 diverse creatives inside. The algorithm handles segmentation via Entity IDs and ARM. |
| **4. Agents Run the System, Humans Set Guardrails** | Claude Code agents cut audit time 60%. But unchecked AI optimizes into failure (the Grok Paradox). Human intuition guides; agents execute. |
| **5. Neural Pre-Testing Replaces Vibes** | Tribe v2 predicts brain activation from any creative. Pre-test before spending. The accounts doing this now have the advantage by May. |

---

## The Loop

The `/gtm` command orchestrates the full lifecycle. The `/gtm-quickstart` command walks you through the 7-day implementation playbook.

```
  ┌──────────────────────────────────────────────────────────────────┐
  │                                                                  │
  │  Phase 1       Phase 2        Phase 3       Phase 4              │
  │ ┌─────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐           │
  │ │DIAGNOSE │→ │ CHANNEL  │→ │  PLAN    │→ │ CREATE   │           │
  │ │EMQ audit│  │ STRATEGY │  │ per      │  │ 20+      │           │
  │ │funnel   │  │ Meta?    │  │ channel  │  │ distinct │           │
  │ │health   │  │ Google?  │  │ budgets  │  │ Entity   │           │
  │ │score    │  │ TikTok?  │  │ targets  │  │ IDs      │           │
  │ └─────────┘  │ Email?   │  │ copy     │  │ 6 hooks  │           │
  │              │ LinkedIn?│  └──────────┘  └──────────┘           │
  │              └──────────┘                                        │
  │                                                                  │
  │  Phase 4.5     Phase 5       Phase 6       Phase 7               │
  │ ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐          │
  │ │ TRIBE V2 │→ │ DEPLOY   │→ │ MEASURE  │→ │ LEARN    │──┐       │
  │ │ neural   │  │ Meta API │  │ PostHog  │  │ save     │  │       │
  │ │ pre-test │  │ Google   │  │ Stripe   │  │ insights │  │       │
  │ │ dead     │  │ Email    │  │ Meta     │  │ update   │  │       │
  │ │ zone     │  │ TikTok   │  │ Google   │  │ memory   │  │       │
  │ │ editing  │  │ Git      │  │ Email    │  │ calibrate│  │       │
  │ └──────────┘  │ (PAUSED) │  │ MER      │  │ Tribe v2 │  │       │
  │               └──────────┘  └──────────┘  └──────────┘  │       │
  │                                                          │       │
  │  ◄───────────────────────────────────────────────────────┘       │
  │   (learnings feed back into next cycle)                          │
  └──────────────────────────────────────────────────────────────────┘
```

---

## Installation

```bash
# Add the marketplace
claude plugins marketplace add DojoCodingLabs/GTM-Engineering-Command-Center

# Install the plugin
claude plugins install gtm-engineering-command-center

# Reload
/reload-plugins
```

Then in your project:

```
/gtm-setup       # Detect your stack, configure credentials
/gtm-quickstart  # 7-day implementation playbook
/gtm             # Full lifecycle orchestrator
```

---

## Slash Commands

### Core Loop

| Command | What It Does |
|---------|-------------|
| `/gtm` | **Full lifecycle orchestrator** — Diagnose → Channel Strategy → Plan → Create → Neural Pre-Test → Deploy → Measure → Learn |
| `/gtm-setup` | First-run wizard — detects 20+ integrations, maps AARRR funnel, creates `.gtm/` config |
| `/gtm-quickstart` | **7-day implementation playbook** — fix data, restructure, create, test, deploy, measure, govern |
| `/gtm-diagnose` | Find the biggest revenue bottleneck. EMQ audit first, then AARRR scoring, Entity ID health check, Blended MER |
| `/gtm-funnel` | Map your AARRR funnel with health scores (0-100) per stage |

### Channel Commands

| Command | What It Does |
|---------|-------------|
| `/gtm-plan` | Multichannel media planning — Meta, Google, TikTok, Email, SEO, LinkedIn, Outreach. Budget-aware structure. |
| `/gtm-create` | Generate 20+ visually distinct creatives across 4 levers and 6 hook categories. Statics, UGC, video, claymation. |
| `/gtm-neurotest` | **Tribe v2 neural pre-test** — brain response prediction, dead zone editing, deploy/test/skip verdicts |
| `/gtm-deploy` | Deploy to any channel — Meta Graph API, Google Ads API, email provider, git commit. ASC+ and Flood+Underbid support. |
| `/gtm-metrics` | Unified metrics from all channels with Blended MER (total spend / total revenue) |
| `/gtm-report` | Weekly performance report with cross-channel attribution and AARRR trend |
| `/gtm-learn` | Extract insights, correlate neural scores with actual CPA, calibrate Tribe v2 weights |

### Specialist Commands

| Command | What It Does |
|---------|-------------|
| `/gtm-email` | Create and deploy email drip campaigns using your project's design system |
| `/gtm-seo` | Technical SEO audit + GEO optimization + programmatic content generation |
| `/gtm-landing` | Generate conversion-optimized landing pages using your component library |
| `/gtm-outreach` | Signal-based cold outreach sequences (Tier 1-2 ethical tactics only) |
| `/gtm-referral` | Design and implement a referral program with K-factor projections |
| `/gtm-experiment` | Structured A/B experiment tracking with statistical significance checks |
| `/gtm-qa` | Autonomous QA — pixel verification, EMQ check, mobile testing, funnel walkthroughs |

### Utility Commands

| Command | What It Does |
|---------|-------------|
| `/gtm-scrape` | Scrape Reddit, X, GitHub for the latest GTM strategies and hacks |
| `/gtm-animate` | Create animated video ads with Remotion |
| `/gtm-routines` | Manage autonomous cloud routines (daily metrics, weekly optimization, PR checks) |

---

## Agents

15 specialized agents. No model pinning — every agent runs on the most capable model in your environment.

| Agent | Role |
|-------|------|
| **funnel-diagnostician** | Cross-channel bottleneck inference engine. EMQ audit, AARRR scoring, Entity ID health, Blended MER. |
| **media-buyer** | Plans campaigns with budget-aware structure (1 ad set at $20/day, ASC+ at $500+/day). Flood+Underbid testing. TikTok + LinkedIn + X.com. Patience Paradox. pLTV bidding. |
| **creative-director** | Generates 20+ visually distinct creatives across 4 levers (Persona × Messaging × Hook × Format) and 6 hook categories. Entity ID diversity. Static priority (60-70% of conversions). AI UGC pipeline. Deliberately absurd formats. |
| **neuro-analyst** | Tribe v2 brain prediction. 7 ROI scores (attention, emotion, memory, decision, comprehension, face response, reward). **Dead Zone Editing** — second-by-second timeline, cut flat signals, front-load peaks. Biological A/B testing. |
| **campaign-operator** | Deploys via Meta Graph API, Google Ads API, email providers. **ASC+ deployment**, Flood+Underbid, Post ID relaunching, EMQ verification post-deploy. |
| **data-analyst** | Unified metrics. Stripe MRR/LTV/churn, email open rates, SEO rankings, ad performance. Cross-channel attribution with Blended MER. |
| **email-marketer** | Designs drip sequences matching your project's existing email design system. Welcome, activation, retention, win-back, upsell. |
| **seo-engineer** | Technical SEO audit, GEO optimization, programmatic content, schema markup. |
| **landing-page-builder** | Generates pages using your project's actual UI library and Tailwind config. Outputs production code. |
| **outreach-operator** | Signal-based cold outreach. Monitors buying signals, generates personalized sequences. Ethical Tier 1-2 only. |
| **referral-architect** | Designs referral programs. K-factor, DB schema + API + UI + email implementation. |
| **stack-detector** | Deep project stack discovery. 20+ integration types → GTM capability mapping. |
| **growth-hacker** | Community intelligence. Reddit, X, GitHub. Compares findings against both Atlas knowledge bases. |
| **qa-engineer** | Autonomous QA via Playwright, Computer Use, Chrome DevTools. Verifies every deployment. |

---

## Skills

16 domain knowledge stacks — the brain that agents reference for decisions.

| Skill | Domain | Key April 2026 Knowledge |
|-------|--------|--------------------------|
| `meta-ads` | Meta Ads API | **Andromeda, Entity Clustering, ARM, EMQ 8+, ASC+, Creative Fatigue Indicator, Attribution Upheaval, Post ID relaunching** |
| `google-ads` | Google Ads | Performance Max, AI Max, Demand Gen, Shopping feed optimization, AI Overviews |
| `email-marketing` | Email drips | Deliverability (SPF/DKIM/DMARC), provider APIs (Resend/SendGrid/Postmark) |
| `seo-engineering` | SEO/GEO | Technical SEO, content strategy, schema markup, AI citation optimization |
| `landing-page-patterns` | Conversion pages | Hero patterns, social proof, CTA optimization, design system integration |
| `irresistible-offer` | Copywriting | **6 Hook Categories**, 30-50+ copy variations per visual, angle mining, brand voice locking |
| `campaign-optimization` | Performance | **Patience Paradox**, Creative Fatigue detection, EMQ monitoring, **Blended MER**, budget scaling rules |
| `posthog-analytics` | PostHog API | HogQL, funnel analysis, cohort creation, dashboard templates |
| `funnel-diagnostics` | AARRR bottlenecks | Bottleneck patterns, correlation rules, benchmarks by vertical |
| `stack-detection` | Project scanning | Provider fingerprints (20+ integrations), framework detection, capability mapping |
| `cross-channel-logic` | Multichannel | **TikTok → Meta → Google funnel**, LinkedIn TLAs, X.com, cross-platform creative reuse, budget by business type |
| `stripe-revenue` | Revenue intel | MRR tracking, cohort revenue, LTV calculation, churn diagnostics |
| `browser-qa` | QA verification | Playwright patterns, Computer Use, verification checklists |
| `neuro-testing` | Brain prediction | Brain region mapping, ROI extraction, score interpretation, dead zone editing, setup guide |

**Plus 2 deep-dive rule files:**
- `andromeda-2026.md` — Full Andromeda mechanics: Entity Clustering, ARM pipeline, EMQ, lifecycle compression, $834M impact study
- `flood-underbid.md` — The contrarian $0 testing method from $80M+ operators

---

## Knowledge Base

Three comprehensive knowledge bases totaling 4,500+ lines:

### GTM Creativity Atlas 2026
1,557 lines. 130+ documented tactics. 15 sections. Ethical ratings for every tactic. Complete tools directory with pricing. Case studies from Dropbox, Calendly, Clay, Loom, Notion.

### Media Buying Atlas April 2026
1,337 lines. Compiled from 13 primary research documents, $834M in analyzed ad spend across 3,014 advertisers, and $100K-$500K/month operator playbooks. Covers:
- Andromeda Entity Clustering and ARM mechanics
- The exact campaign structure that $100K-$500K/month accounts run
- ASC+ optimization (62% of ecom spend, 22% ROAS improvement)
- Creative Fatigue Indicator (new April 2026)
- Flood + Underbid contrarian testing ($0 testing at massive scale)
- Tribe v2 Dead Zone Editing workflow
- TikTok, LinkedIn Thought Leader Ads, X.com benchmarks
- Cross-platform budget allocation by business type
- AI UGC pipeline ($28K/day accounts running synthetic avatars)
- Peter Thiel contrarian plays (Patience Paradox, static images > video)
- Complete Whitehat/Grayhat/Blackhat ethical ranking matrix
- 7-day implementation playbook

### AARRR Framework Reference
Industry benchmarks by vertical (developer tools, B2B SaaS, consumer, marketplace). Funnel health scoring algorithm. Cross-stage correlation patterns with diagnostic prescriptions.

---

## Tribe v2 Neural Pre-Testing

The plugin integrates Meta's open-source brain prediction model to score creatives BEFORE deployment:

```
/gtm-create    →  Generate 20+ visually distinct creatives
                     │
/gtm-neurotest →  Tribe v2 scores each creative:
                     │
                     │  Creative     Attn  Emot  Mem   Decn  Composite  Verdict
                     │  ─────────── ───── ───── ───── ───── ──────────  ───────
                     │  pain_point    82    71    65    78     75.3      DEPLOY
                     │  social_proof  91    58    72    69     73.8      DEPLOY
                     │  speed         73    62    48    61     62.1      TEST
                     │  outcome       67    45    51    55     55.6      SKIP
                     │
                     │  Dead zones at 0:04-0:07: CUT. Front-load peak from 0:08.
                     │
/gtm-deploy    →  Only DEPLOY + TEST creatives get budget
                     Budget saved: 40-60% (losers never spend)
```

Three execution modes: Local GPU (fast), Local CPU (slower), Google Colab (free GPU).

After campaigns run, `/gtm-learn` correlates neural scores with actual CPA/CTR and calibrates the composite weights — the system gets smarter every cycle.

---

## Andromeda-Native Campaign Structure

The plugin structures campaigns the way $100K-$500K/month operators run them in April 2026:

| Budget | Structure | Why |
|--------|-----------|-----|
| Under $50/day | 1 campaign, 1 ad set, 15-20 creatives | Can't exit learning with multiple ad sets |
| $50-$100/day | 1 campaign, 1-2 ad sets, 20+ creatives | One broad + one retargeting |
| $100-$500/day | 1 campaign, 2-3 ad sets, 10+ creatives each | One per persona + landing page |
| $500+/day | ASC+ (60-70%) + CBO testing (20-30%) + retargeting (10-15%) | Full Advantage+ Shopping |

**Flood + Underbid** (contrarian testing): 1 CBO, 100+ creatives, low bid cap. Losers spend nothing. Winners self-select. Basically testing for free.

**Patience Paradox**: If CPA ≤ 1.2x target for 5 straight days — LOCK the ad set. No edits for 14 days. Let Andromeda compound.

---

## Routines

Cloud-based autonomous workflows powered by [Claude Code Routines](https://code.claude.com/docs/en/routines).

| Routine | Trigger | What It Does |
|---------|---------|-------------|
| **Daily Metrics Pull** | 9 AM daily | Pulls all channel metrics, saves snapshot, alerts on EMQ drops and CPA spikes |
| **Weekly Optimization** | Monday 10 AM | Full learning loop + funnel diagnosis + weekly report |
| **PR Conversion Check** | GitHub PR event | Reviews landing/email PRs for tracking completeness |
| **Experiment Monitor** | 6 PM daily | Checks A/B experiments for statistical significance |

---

## Stack Detection

`/gtm-setup` auto-detects 20+ integration types:

```
Full Stack Detection — 21 integrations detected

| Category       | Integration       | Details                                    |
|----------------|-------------------|--------------------------------------------|
| Email          | Resend            | 22 templates, drip scheduler, 3 domains    |
| Analytics      | PostHog + GA4     | 113+ events, 17 categories, /ph proxy      |
| Ads            | Meta Pixel + CAPI | Dual tracking, consent-gated, event dedup  |
| Payments       | Stripe            | 3 tiers, 13 Edge Functions, webhooks       |
| Design System  | Tailwind + Custom | 66+ components, #C980FC/#FF7151/#07070E    |
| SEO            | Custom seoService | 50+ methods, 9 sitemap routes, JSON-LD     |
| Deployment     | Vercel            | CSP headers, PostHog proxy                 |
| Video          | Mux               | Signed playback, uploader, webhooks        |
| Error Tracking | Sentry            | Frontend + backend, env tagging            |
| Feature Flags  | PostHog           | Dashboard-managed                          |
| Auth           | Supabase Auth     | Email + GitHub + Discord + Google + LinkedIn|
| Database       | Supabase/PG       | 517 migrations, full RLS                   |
| Real-time      | Supabase Realtime | Forum + hackathon live updates             |

AARRR Funnel Health:
  Acquisition:  ████████░░ 75  [STRONG]
  Activation:   ███████░░░ 70  [STRONG]
  Retention:    █████░░░░░ 45  [MODERATE]
  Revenue:      ████████░░ 80  [STRONG]
  Referral:     ██░░░░░░░░ 15  [WEAK] ← biggest gap
```

---

## The 7-Day Quickstart

`/gtm-quickstart` walks you through the highest-impact implementation:

| Day | Focus | What Happens |
|-----|-------|-------------|
| **Day 1** | Fix Data Layer | CAPI + EMQ audit. Every Purchase event gets email + phone + click ID. |
| **Day 2** | Restructure | Consolidate to ASC+ + CBO + retargeting. Kill the old funnel. |
| **Day 3** | Creative Production | 20-30 distinct Entity IDs. 4 levers × 6 hooks. Statics + UGC + absurd. |
| **Day 4** | Agentic Workflows | Daily metrics, fatigue scan, bleed check, rebalance automation. |
| **Day 5** | Neural Pre-Test | Tribe v2 scores all creatives. Dead zone editing. Deploy winners only. |
| **Day 6** | Cross-Platform | Meta winners → Google Demand Gen + YouTube Shorts + TikTok Spark Ads. |
| **Day 7** | Governance | Blended MER dashboard. Hard rules. Patience Paradox for winners. |

---

## Requirements

| Requirement | Details |
|---|---|
| **Claude Code** | Latest version with plugin support |
| **Meta Ads** | Optional — System User token from live-mode Business app |
| **Google Ads** | Optional — Customer ID + developer token |
| **TikTok Ads** | Optional — Business account for Spark Ads |
| **PostHog** | Optional — Project + Personal API keys for diagnostics |
| **Stripe** | Optional — For revenue diagnostics (MRR, LTV, churn) |
| **Gemini API** | Optional — For Nano Banana 2 creative generation |
| **Tribe v2** | Optional — Python 3.11+ with GPU for neural pre-testing |
| **Email Provider** | Optional — Resend, SendGrid, or Postmark API key |

The plugin works with whatever you have configured. No channel is required — it adapts.

---

## Philosophy

> *A single GTM Engineer with the right agentic stack in 2026 can outperform a 10-person traditional sales and marketing team.*

This plugin is that stack. It's not a tool — it's an autonomous growth team:

- **Media Buyer** who understands Andromeda and structures campaigns the way $100K/mo operators do
- **Creative Director** who generates 20+ visually distinct Entity IDs, not 5 text variations
- **Neuro Analyst** who predicts brain response and edits dead zones before you spend a dollar
- **Data Analyst** who correlates metrics across every channel and calculates Blended MER
- **Growth Hacker** who scrapes the internet for strategies the Atlas hasn't documented yet
- **Email Marketer** who builds drip campaigns matching your design system
- **SEO Engineer** who audits technical SEO and optimizes for AI citations
- **Landing Page Builder** who writes production code using your component library
- **QA Engineer** who verifies everything works in a real browser
- **Funnel Diagnostician** who finds exactly where money is leaking — EMQ first, then AARRR

Human approves. Agent executes. Revenue grows.

---

## Contributing

PRs welcome. This is open source under MIT.

```bash
git clone https://github.com/DojoCodingLabs/GTM-Engineering-Command-Center.git
```

---

## License

MIT — see [LICENSE](./LICENSE).

<p align="center">
  Built by <a href="https://dojocoding.com">Dojo Coding Labs</a>
</p>
