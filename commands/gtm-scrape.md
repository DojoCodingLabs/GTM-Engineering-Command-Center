---
name: gtm-scrape
description: "Scrape Reddit, X, GitHub for GTM strategies and hacks"
argument-hint: ""
---

# Community Intelligence Command

You are the growth-hacker agent. You will search Reddit, X (Twitter), and GitHub for the latest GTM strategies, paid ads hacks, and Meta Ads insights. You will distill the findings into actionable strategies and save them to the project's knowledge base.

## Phase 0: Pre-Flight Check

1. Read `.gtm/config.json` in the project root.
   - If the file does not exist, tell the user: "GTM Command Center is not set up. Run `/gtm-setup` first." Then STOP.
2. Read `.gtm/MEMORY.md` to see what community strategies have already been captured.
3. Read existing strategies from `.gtm/strategies/` to avoid duplicating known intel.
4. Load product context from `config.product` for relevance filtering.

## Phase 1: Reddit Intelligence

Search the following subreddits for recent high-value discussions. Use web search tools or the Firecrawl MCP to access content.

### 1.1: Target Subreddits

| Subreddit | Focus |
|-----------|-------|
| r/PPC | General paid advertising strategies |
| r/FacebookAds | Meta-specific tactics and troubleshooting |
| r/digital_marketing | Broad digital marketing strategies |
| r/Entrepreneur | Growth strategies for startups |
| r/SaaS | SaaS-specific GTM patterns (if product is SaaS) |
| r/growthacking | Growth hacking techniques |

### 1.2: Search Queries

For each subreddit, search for recent posts (last 30 days) with these query patterns:
- "Meta ads" + "low CPA"
- "Facebook ads" + "2025" or "2026" (current year strategies)
- "ad creative" + "winning"
- "scaling" + "campaigns"
- "cost per acquisition" + "reduce"
- "dynamic creative" + "results"
- "Advantage+" + "performance"
- "lookalike" + "audience"
- "{product_category}" + "ads" (based on the user's product type)

### 1.3: Extract from Reddit

For each relevant post/comment, extract:
- **Strategy name**: One-line summary
- **Source**: Subreddit + post title + URL
- **Tactic**: What specifically to do
- **Reported results**: Any metrics shared (CPA reduction, ROAS improvement, etc.)
- **Applicability**: How relevant is this to the user's product/budget level
- **Risk level**: Low (proven) / Medium (anecdotal) / High (experimental)

Filter out:
- Posts with low engagement (<10 upvotes)
- Purely promotional content
- Strategies that require budgets 10x above the user's
- Outdated tactics (explicitly from pre-2024)

## Phase 2: X (Twitter) Intelligence

Search X for trending Meta Ads and GTM content.

### 2.1: Search Queries

Use web search to find recent X posts with these queries:
- `#MetaAds` + tips/tricks/hack
- `#FacebookAds` + results/winning
- `#PaidSocial` + strategy
- `"ad creative"` + `"game changer"`
- `"CPA"` + `"dropped"` or `"reduced"`
- `"ROAS"` + `"increased"` or `"improved"`
- Notable accounts: Search for threads from known paid media experts

### 2.2: Extract from X

For each relevant post/thread:
- **Strategy name**: One-line summary
- **Source**: Author + post URL
- **Tactic**: The specific actionable advice
- **Context**: Budget level, product type, or industry mentioned
- **Engagement**: Likes/reposts (proxy for community validation)

Filter out:
- Ads/promoted content selling courses
- Generic motivational content without tactics
- Strategies with no specifics ("just test more bro")

## Phase 3: GitHub Intelligence

Search GitHub for Claude Code GTM repositories and Meta Ads automation tools.

### 3.1: Search Queries

Search GitHub (via web search or GitHub API) for:
- `claude code GTM` or `claude code marketing`
- `meta ads api automation`
- `facebook ads python` (popular libraries/tools)
- `ad creative generation AI`
- `campaign optimization script`
- `.claude` + `marketing` or `ads` (Claude Code plugins for marketing)

### 3.2: Extract from GitHub

For each relevant repository:
- **Repository**: Name + URL
- **What it does**: Brief description
- **Useful patterns**: Code patterns, API usage, automation approaches
- **Stars/activity**: Indicator of community trust
- **Applicability**: Can we use or adapt this?

Focus on:
- Automation scripts for Meta Ads API
- Creative generation pipelines
- Analytics/reporting tools
- Campaign optimization algorithms
- Claude Code plugins for GTM

## Phase 4: Distill Strategies

Organize all findings into actionable strategy documents.

### 4.1: Categorize

Group strategies into categories:
1. **Creative Strategies**: New ad creative approaches, formats, angles
2. **Targeting Strategies**: Audience building, segmentation, exclusions
3. **Bidding & Budget**: Bid strategies, budget optimization, scaling techniques
4. **Campaign Structure**: How to organize campaigns, ad sets, naming conventions
5. **Landing Page**: Conversion optimization, pre-sell pages, bridge pages
6. **Automation**: Scripts, tools, workflows for efficiency
7. **Platform Updates**: New Meta features, algorithm changes, policy updates

### 4.2: Rank by Priority

For each strategy, assign:
- **Impact**: High/Medium/Low (potential effect on KPIs)
- **Effort**: High/Medium/Low (how hard to implement)
- **Relevance**: How well it fits the user's product and budget
- **Priority Score**: Impact x (1/Effort) x Relevance

### 4.3: Actionable Playbooks

For the top 5 strategies, create mini-playbooks:
```
## Strategy: {Name}
Source: {Reddit/X/GitHub link}
Priority: {score}

### What
{1-2 sentence description}

### Why It Works
{Reasoning or reported evidence}

### How to Implement
1. {Step 1}
2. {Step 2}
3. {Step 3}

### Expected Impact
{Estimated effect on CPA/ROAS/CTR}

### Risk
{What could go wrong, how to mitigate}
```

## Phase 5: Save Strategies

### 5.1: Strategy Files

Save to `.gtm/strategies/scrape-{YYYY-MM-DD}.md`:

```markdown
# Community Intelligence Report — {date}

## Sources Scanned
- Reddit: {X} posts across {Y} subreddits
- X: {X} posts/threads
- GitHub: {X} repositories

## Top Strategies Found

### 1. {Strategy Name}
{playbook from Phase 4.3}

### 2. {Strategy Name}
{playbook}

...

## All Findings

### Creative Strategies
{list}

### Targeting Strategies
{list}

### Bidding & Budget
{list}

### Other
{list}

---
Scraped by GTM Command Center on {timestamp}
```

### 5.2: Update MEMORY.md

Append to the "Community Strategies" section of `.gtm/MEMORY.md`:

```markdown
## Community Strategies
- [{date}] {strategy 1 one-liner} (source: {subreddit/account})
- [{date}] {strategy 2 one-liner}
- [{date}] {strategy 3 one-liner}
```

## Phase 6: Output

Present findings to the user:

```
Community Intelligence Scan Complete — {date}

Sources: {X} Reddit posts | {Y} X posts | {Z} GitHub repos

Top 5 Strategies Found:
1. {name} — {one-liner} [Impact: High, Effort: Low]
2. {name} — {one-liner} [Impact: High, Effort: Medium]
3. {name} — {one-liner} [Impact: Medium, Effort: Low]
4. {name} — {one-liner} [Impact: Medium, Effort: Medium]
5. {name} — {one-liner} [Impact: Medium, Effort: Medium]

Full report: .gtm/strategies/scrape-{date}.md

Want to test any of these strategies? Say the number and I'll
incorporate it into your next /gtm-plan.
```

## Error Handling

- **Web search unavailable**: If no web search or Firecrawl MCP tools are available, tell the user: "Web search tools are not available in this session. Install the Firecrawl plugin or enable web search to use this command." STOP.
- **Rate limiting on search**: If search APIs rate-limit, reduce the number of queries and report partial results.
- **No relevant results**: If searches return nothing useful, report: "No high-quality strategies found for the current queries. Try again in a week, or suggest specific topics to search for."
- **Duplicate strategies**: If a found strategy already exists in `.gtm/strategies/`, skip it and note: "Strategy '{name}' already captured on {date}."
