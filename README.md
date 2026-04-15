# GTM Engineering Command Center

**Turn Claude Code into your autonomous GTM engineer.**

Plan media buys, generate ad creatives, deploy campaigns to Meta Ads, analyze metrics with PostHog, and run self-learning optimization loops -- all from your terminal.

---

## What It Does

The GTM Engineering Command Center transforms Claude Code into a full-stack growth engineering system. It operates as an autonomous loop:

```
Plan --> Create --> Deploy --> Measure --> Learn
  ^                                         |
  |_________________________________________|
```

1. **Plan** -- Build media plans with budget allocation, audience targeting, and placement strategy using the Irresistible Offer framework.
2. **Create** -- Generate ad creatives (images, copy, hooks) using Nano Banana 2 powered by Google Gemini's image generation.
3. **Deploy** -- Push campaigns live to Meta Ads (Facebook + Instagram) via the Marketing API. Handles ad accounts, campaigns, ad sets, and ads.
4. **Measure** -- Pull performance metrics from PostHog and Meta Ads. Analyze ROAS, CPA, CTR, and conversion funnels.
5. **Learn** -- Extract insights from campaign data and persist them to `.gtm/MEMORY.md`. Every future campaign benefits from past learnings.

---

## Slash Commands

| Command | Description |
|---|---|
| `/gtm-setup` | Initialize `.gtm/` directory, validate API credentials, configure project settings |
| `/gtm-plan` | Generate a media plan with budget, audiences, placements, and schedule |
| `/gtm-creative` | Create ad creatives using Nano Banana 2 (Gemini image generation) |
| `/gtm-deploy` | Deploy a campaign to Meta Ads -- creates campaign, ad sets, and ads |
| `/gtm-metrics` | Pull and analyze campaign performance from Meta Ads and PostHog |
| `/gtm-optimize` | Analyze active campaigns and recommend budget shifts, pauses, or scaling |
| `/gtm-learn` | Extract insights from campaign data and persist to GTM memory |
| `/gtm-report` | Generate a formatted performance report (daily, weekly, or custom range) |
| `/gtm-scrape` | Research competitor ads, landing pages, and community strategies |
| `/gtm-status` | Show current campaign status, spend, and key metrics at a glance |

---

## Agents

| Agent | Description |
|---|---|
| `media-planner` | Builds media plans using the Irresistible Offer framework. Allocates budget across audiences and placements based on historical performance. |
| `creative-engine` | Generates ad creatives (images + copy) using Nano Banana 2 methodology. Produces hooks, body copy, CTAs, and image prompts for Gemini. |
| `campaign-deployer` | Handles Meta Ads API integration. Creates campaigns, ad sets, ads, and manages audience targeting and bid strategies. |
| `metrics-analyst` | Pulls data from PostHog and Meta Ads. Computes ROAS, CPA, CTR, frequency, and identifies winning/losing segments. |
| `optimization-loop` | Orchestrates the learn-and-improve cycle. Reads campaign data, extracts patterns, updates GTM memory, and suggests next actions. |

---

## Requirements

| Requirement | Details |
|---|---|
| **Claude Code** | v1.0.0 or later |
| **Meta Business Account** | With a configured Ad Account, Page, and Pixel. System User token with `ads_management` and `ads_read` permissions. |
| **PostHog** | Project with API key. Used for product analytics and conversion tracking. |
| **Gemini API Key** | Google AI Studio API key for Nano Banana 2 creative generation (image model: `gemini-3.1-flash-image-preview`). |

---

## Installation

```bash
claude plugins install DojoCodingLabs/GTM-Engineering-Command-Center
```

---

## Quick Start

1. Install the plugin (see above).
2. Run the setup command in your project directory:

```
/gtm-setup
```

This will:
- Create the `.gtm/` directory with config, memory, and subdirectories
- Prompt you to fill in your Meta, PostHog, and Gemini credentials
- Validate API connectivity
- Configure your project details (name, URL, design tokens)

3. Create your first media plan:

```
/gtm-plan
```

4. Generate creatives for the plan:

```
/gtm-creative
```

5. Deploy to Meta Ads:

```
/gtm-deploy
```

6. Check performance:

```
/gtm-metrics
```

---

## Architecture

```
GTM-Engineering-Command-Center/
|
|-- .claude-plugin/
|   |-- plugin.json              # Plugin manifest
|   +-- marketplace.json         # Marketplace metadata
|
|-- commands/                    # Slash command definitions
|   |-- gtm-setup.md
|   |-- gtm-plan.md
|   |-- gtm-creative.md
|   |-- gtm-deploy.md
|   |-- gtm-metrics.md
|   |-- gtm-optimize.md
|   |-- gtm-learn.md
|   |-- gtm-report.md
|   |-- gtm-scrape.md
|   +-- gtm-status.md
|
|-- agents/                      # Agent definitions
|   |-- media-planner.md
|   |-- creative-engine.md
|   |-- campaign-deployer.md
|   |-- metrics-analyst.md
|   +-- optimization-loop.md
|
|-- skills/                      # Domain knowledge & rules
|   |-- irresistible-offer/      # Offer framework methodology
|   |-- meta-ads/                # Meta Marketing API patterns
|   |-- posthog-analytics/       # PostHog query patterns
|   |-- campaign-optimization/   # Optimization heuristics
|   +-- gtm-atlas/               # GTM strategy knowledge base
|
|-- hooks/                       # Lifecycle hooks
|
|-- templates/
|   |-- init/                    # Project initialization template
|   |   +-- .gtm/
|   |       |-- config.json      # API credentials (gitignored)
|   |       |-- MEMORY.md        # Persistent GTM learnings
|   |       |-- .gitignore
|   |       |-- learnings/       # Campaign insight files
|   |       |-- metrics/         # Metric snapshots
|   |       |-- creatives/       # Generated ad creatives
|   |       |-- strategies/      # Media strategies
|   |       |-- plans/           # Media plans
|   |       +-- campaigns/       # Campaign deployment records
|   +-- dashboards/              # Report templates
|
+-- scripts/                     # Utility scripts


Data Flow:

  +------------------+
  |   /gtm-plan      |---> media-planner agent
  +------------------+         |
                               v
  +------------------+   .gtm/plans/
  |  /gtm-creative   |---> creative-engine agent
  +------------------+         |
                               v
  +------------------+   .gtm/creatives/
  |  /gtm-deploy     |---> campaign-deployer agent
  +------------------+         |
                               v
                         Meta Ads API
                               |
  +------------------+         v
  |  /gtm-metrics    |---> metrics-analyst agent
  +------------------+    (Meta Ads + PostHog)
                               |
                               v
  +------------------+   .gtm/metrics/
  |  /gtm-learn      |---> optimization-loop agent
  +------------------+         |
                               v
                         .gtm/MEMORY.md
                          (feeds back into
                           future /gtm-plan)
```

---

## Project Structure (User's Repo)

After running `/gtm-setup`, your project will contain:

```
your-project/
+-- .gtm/
    |-- config.json       # API credentials (gitignored)
    |-- MEMORY.md         # Accumulated GTM learnings
    |-- .gitignore
    |-- learnings/        # Insight files from /gtm-learn
    |-- metrics/          # Metric snapshots from /gtm-metrics
    |-- creatives/        # Generated images and copy
    |-- strategies/       # High-level strategy documents
    |-- plans/            # Media plans from /gtm-plan
    +-- campaigns/        # Deployment records from /gtm-deploy
```

---

## How the Learning Loop Works

Every time you run `/gtm-learn`, the optimization-loop agent:

1. Reads the latest campaign metrics from `.gtm/metrics/`
2. Compares performance against historical baselines in `.gtm/learnings/`
3. Identifies patterns (winning audiences, best-performing hooks, optimal bid strategies)
4. Appends structured insights to `.gtm/MEMORY.md`
5. Creates a dated insight file in `.gtm/learnings/`

When you next run `/gtm-plan` or `/gtm-creative`, the media-planner and creative-engine agents read `MEMORY.md` first, so every campaign iteration is informed by past results.

---

## License

MIT -- see [LICENSE](./LICENSE).

Built by [Dojo Coding Labs](https://dojocoding.io).
