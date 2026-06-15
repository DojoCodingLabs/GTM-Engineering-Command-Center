---
name: gtm-metrics
description: "Pull and analyze metrics from Meta, Stripe, Email, SEO, and Google Ads"
argument-hint: "--auto (for routine mode) or channel (meta/stripe/email/seo/google/all)"
---

# Unified Metrics Analysis Command

You are the data-analyst agent. You will pull performance data from all configured channels -- Meta Ads, Stripe, email provider, SEO/organic, and Google Ads -- cross-reference attribution, build a unified dashboard, and generate optimization recommendations.

## Phase 0: Pre-Flight Check

1. Read `.gtm/config.json` in the project root.
   - If the file does not exist, tell the user: "GTM Command Center is not set up. Run `/gtm-setup` first." Then STOP.
2. Determine which data sources are configured:
   - `.env.gtm` contains `ACCESS_TOKEN` + `AD_ACCOUNT_ID` AND `meta` CLI on PATH -> Meta Ads insights available
   - `posthog.personal_api_key` + `posthog.project_id` -> PostHog analytics available
   - `stripe.secret_key` -> Stripe revenue data available
   - `email.api_key` + `email.provider` -> Email metrics available
   - `google_ads.customer_id` present AND `command -v google-ads-open-cli` (binary on PATH) AND a `google-ads-open-cli customers --format compact` smoke test exits 0 -> Google Ads insights available. If the binary is missing, note "Google Ads CLI not installed -- run `npm install -g google-ads-open-cli`" and skip the channel. If the smoke test fails on auth (see normalized exit handling, Phase 5), note "Google Ads auth expired -- run `google-ads-open-cli auth login`" and skip.
3. Test each configured API's connectivity (Meta: `meta auth status`; Google Ads: `google-ads-open-cli customers` smoke test from step 2; PostHog/Stripe/etc.: respective health endpoints).
4. If `--auto` flag is present (routine mode): skip interactive prompts, pull all available data, save snapshot, check thresholds, and output alerts only.
5. Load existing deployment records from `.gtm/campaigns/` to know which campaigns to query.
   - If no deployment records exist, query accounts directly for all active/recent campaigns.

## Phase 1: Pull Meta Ads Insights

If Meta Ads is configured, use the **`meta ads insights get`** CLI. The CLI handles auth, pagination, and JSON formatting. Full reference: `skills/meta-ads/rules/ads-cli.md`.

### 1.1: Account-Level Overview

```bash
meta ads insights get \
  --date-preset last_7d \
  --fields spend,impressions,clicks,cpc,cpm,ctr,actions,cost_per_action_type,conversions,purchase_roas \
  --output json
```

### 1.2: Campaign-Level Breakdown

```bash
meta ads insights get \
  --date-preset last_7d \
  --fields campaign_id,campaign_name,spend,impressions,clicks,cpc,cpm,ctr,actions,cost_per_action_type,conversions \
  --output json
```

To filter to active/recent campaigns only, post-filter the JSON with `jq` (the CLI does not yet expose a `--filtering` flag for delivery status):

```bash
meta ads insights get ... --output json | jq '[.[] | select(.spend != null and (.spend | tonumber) > 0)]'
```

### 1.3: Ad Set and Ad Level Breakdowns

```bash
# Per ad set
meta ads insights get --campaign-id "$CAMPAIGN_ID" --date-preset last_7d --output json

# Per ad (creative performance)
meta ads insights get --adset-id "$ADSET_ID" --date-preset last_7d \
  --fields ad_name,ad_id,impressions,clicks,spend,cpc,ctr,actions,video_p25_watched_actions,video_p100_watched_actions \
  --output json
```

### 1.4: Exit Code Handling (especially in `--auto` / routine mode)

```bash
meta ads insights get ... --output json > /tmp/insights.json
case $? in
  0) ;;
  3) echo "ALERT: ACCESS_TOKEN expired"; exit 3 ;;
  4) sleep 30; meta ads insights get ... --output json > /tmp/insights.json || { echo "Persistent API error"; exit 4; } ;;
esac
```

### 1.5: Parse Actions

Extract from Meta's action arrays:
- `link_click`, `landing_page_view`, `lead`, `purchase`
- `offsite_conversion.fb_pixel_lead`, `offsite_conversion.fb_pixel_purchase`

Calculate derived metrics:
- **CPA** = spend / conversions
- **ROAS** = revenue / spend
- **Landing Page View Rate** = landing_page_views / clicks
- **Conversion Rate** = conversions / landing_page_views

## Phase 2: Pull Stripe Revenue Data

If Stripe is configured:

### 2.1: MRR Calculation

Query Stripe API for active subscriptions:
- List all active subscriptions
- Sum monthly recurring revenue
- Calculate MRR growth vs. previous period

### 2.2: Churn Rate

- Count subscriptions canceled in the period
- Calculate monthly churn rate: canceled / active at period start
- Calculate revenue churn: lost MRR / starting MRR

### 2.3: LTV Estimation

- Average revenue per user (ARPU): MRR / active subscribers
- Estimated LTV: ARPU / monthly churn rate
- LTV:CAC ratio: LTV / CPA (from Meta or blended)

### 2.4: New Revenue Attribution

- New customers in the period
- Revenue from new customers
- Revenue from existing customers (upgrades, expansions)
- Refunds and disputes

Present Stripe metrics:
```
Stripe Revenue Metrics (last 7 days):

| Metric | Value | vs. Last Week |
|--------|-------|---------------|
| MRR | $X | {+/-}% |
| New Customers | {N} | {+/-}% |
| Churn Rate | X% | {+/-}pp |
| ARPU | $X | {+/-}% |
| LTV | $X | {+/-}% |
| LTV:CAC | X:1 | {+/-} |
| Net Revenue | $X | {+/-}% |
```

## Phase 3: Pull Email Metrics

If an email provider is configured:

### 3.1: Provider-Specific Metrics

**Resend**: Query Resend API for email stats:
- Sent, delivered, opened, clicked, bounced
- Per-email and per-sequence performance

**SendGrid**: Query SendGrid Stats API:
- Delivered, opens, clicks, bounces, unsubscribes
- Engagement rates by campaign/automation

**Postmark**: Query Postmark Stats API:
- Similar metrics per message stream

### 3.2: Email Performance Summary

```
Email Metrics (last 7 days):

| Sequence | Sent | Delivered | Opened | Clicked | Conv |
|----------|------|-----------|--------|---------|------|
| Welcome | {N} | {N} ({%}) | {N} ({%}) | {N} ({%}) | {N} ({%}) |
| Activation | {N} | {N} ({%}) | {N} ({%}) | {N} ({%}) | {N} ({%}) |
| Retention | {N} | {N} ({%}) | {N} ({%}) | {N} ({%}) | {N} ({%}) |

Overall:
  Open Rate: {X}% (industry avg: 20-30%)
  Click Rate: {X}% (industry avg: 2-5%)
  Unsubscribe Rate: {X}% (should be <0.5%)
```

## Phase 4: Pull SEO/Organic Metrics

If PostHog or Google Search Console data is available:

### 4.1: Organic Traffic

Query PostHog for non-paid traffic:
- Filter: `$utm_source != "meta"` AND `$utm_source != "google_ads"`
- Pageviews, unique visitors, sessions
- Top landing pages by organic traffic

### 4.2: Search Performance (if GSC configured)

If Google Search Console API access is available:
- Total impressions, clicks, average position
- Top queries by clicks
- Top pages by clicks
- Click-through rate from search

### 4.3: SEO Content Performance

If `.gtm/seo/content/` was deployed:
- Track page views for each SEO content piece
- Compare to pre-deployment baseline (if available)

Present:
```
SEO/Organic Metrics (last 7 days):

| Metric | Value | vs. Last Week |
|--------|-------|---------------|
| Organic Visitors | {N} | {+/-}% |
| Top Organic Page | {page} | {N} views |
| Avg. Time on Page | {X}s | {+/-}% |
| Organic Conversions | {N} | {+/-}% |
```

## Phase 5: Pull Google Ads Metrics

If Google Ads is configured, use the **`google-ads-open-cli`** (READ-ONLY) for all pulls here. The CLI never mutates -- any fix surfaced below (negatives, pauses, budget cuts) goes through the REST `:mutate` write path, not this command. Full reference: `skills/google-ads/rules/gads-cli.md`.

**MICROS, ALWAYS.** Every cost field the CLI returns -- `cost_micros`, `average_cpc`, `average_cpm` -- is in micros. **1,000,000 micros = $1.** Divide by `1e6` before reporting dollars or computing CPA/ROAS. This is the Google analog of Meta's "spend is in cents" gotcha, except the multiplier is a million. A single skipped division is a 1,000,000x reporting error. GAQL `WHERE` clauses filter on raw micros (e.g. `cost_micros > 50000000` = $50).

Set `CID` to the 10-digit customer id from `google_ads.customer_id`, **dashes stripped**. Set the window to match the Meta phase (`--start`/`--end` for last 7 days). All calls use `--format compact` (NDJSON) for `jq`.

### 5.0: Normalized Exit Handling (`--auto` / routine mode)

This is a **different binary from `meta`** -- do NOT assume Meta's literal `0/3/4` codes. The read CLI only gives you `rc != 0` plus stderr text. Capture stderr, classify by regex, re-emit the plugin's normalized codes (`3`=auth, `4`=API). Use the `gads_read` wrapper from `skills/google-ads/rules/gads-cli.md` §6:

```bash
gads_read() {
  local out="$1"; shift
  local err; err="$(mktemp)"
  google-ads-open-cli "$@" --format compact > "$out" 2> "$err"
  local rc=$?
  if [ $rc -ne 0 ]; then
    if grep -qiE 'auth|token|credential|unauthenticated|permission' "$err"; then
      echo "AUTH ERROR: re-run 'google-ads-open-cli auth login'" >&2; cat "$err" >&2; rm -f "$err"; return 3
    else
      echo "API ERROR: backoff + retry once" >&2; cat "$err" >&2; rm -f "$err"; return 4
    fi
  fi
  rm -f "$err"; return 0
}

gads_read /tmp/gads_camps.ndjson campaign-stats "$CID" --start "$START" --end "$END"
case $? in
  0) : ;;  # parse /tmp/gads_camps.ndjson
  3) echo "ALERT: Google Ads auth expired -- run google-ads-open-cli auth login (or refresh GOOGLE_ADS_ACCESS_TOKEN)"; exit 3 ;;
  4) sleep 30; gads_read /tmp/gads_camps.ndjson campaign-stats "$CID" --start "$START" --end "$END" || { echo "Persistent Google Ads API error"; exit 4; } ;;
esac
```

In interactive mode, the same auth/API distinction applies but you may prompt the operator instead of exiting.

### 5.1: Account + Per-Campaign Overview

`campaign-stats` returns the default metric set: `impressions, clicks, cost_micros, conversions, conversions_value, ctr, average_cpc, average_cpm, interactions, all_conversions`.

```bash
# Per-campaign breakdown (last 7d)
gads_read /tmp/gads_camps.ndjson campaign-stats "$CID" --start "$START" --end "$END"

# Account overview = roll up the per-campaign rows (cost_micros -> dollars)
jq -s '
  { spend:        ((map(.metrics.costMicros|tonumber)|add)/1000000),
    impressions:  (map(.metrics.impressions|tonumber)|add),
    clicks:       (map(.metrics.clicks|tonumber)|add),
    conversions:  (map(.metrics.conversions|tonumber)|add),
    conv_value:   (map(.metrics.conversionsValue|tonumber)|add) }
  | . + { cpa:  (if .conversions > 0 then .spend/.conversions else null end),
          roas: (if .spend > 0 then .conv_value/.spend else null end) }
' /tmp/gads_camps.ndjson
```

Per-campaign CPA = `cost_micros/1e6 / conversions`; ROAS = `conversions_value / (cost_micros/1e6)`. Optionally add `--segments device,ad_network_type` to split Search vs Display/PMax and desktop vs mobile.

### 5.2: Ad Group + Keyword Stats

```bash
# Ad-group grain (find dead ad groups)
gads_read /tmp/gads_adgroups.ndjson ad-group-stats "$CID" --start "$START" --end "$END"

# Keyword grain (match-type performance, dead keywords)
gads_read /tmp/gads_keywords.ndjson keyword-stats "$CID" --start "$START" --end "$END"
```

Rank ad groups and keywords by spend (`cost_micros/1e6`) and conversions. Zero-conversion, high-cost keywords are negative/pause candidates -- the fix is a REST `:mutate`, never this CLI.

### 5.3: Search-Term / N-Gram Top Converters + Waste (GAQL)

The convenience commands do not cover `search_term_view`; use raw `query`. Pull 30-day search terms with cost + conversions:

```bash
gads_read /tmp/gads_terms.ndjson query "$CID" "
  SELECT
    search_term_view.search_term,
    metrics.cost_micros,
    metrics.conversions,
    metrics.clicks
  FROM search_term_view
  WHERE segments.date DURING LAST_30_DAYS
  ORDER BY metrics.cost_micros DESC
"
```

**Top converters** -- search terms with the most conversions (winners to mine for new exact-match keywords):

```bash
jq -s '
  map({ term: .searchTermView.searchTerm,
        spend: ((.metrics.costMicros|tonumber)/1000000),
        conv:  (.metrics.conversions|tonumber) })
  | map(select(.conv > 0))
  | sort_by(-.conv)
  | .[0:10]
' /tmp/gads_terms.ndjson
```

**Waste n-grams** -- tokenize each term into 1- and 2-grams, roll up cost (÷1e6) and conversions per token, keep zero-conversion / spend>$25 grams (negative-keyword candidates):

```bash
jq -rc '
  (.searchTermView.searchTerm) as $t
  | ($t | ascii_downcase | gsub("[^a-z0-9 ]";"") | split(" ")) as $w
  | { unigrams: $w,
      bigrams: [ range(0; ($w|length)-1) | "\($w[.]) \($w[.+1])" ],
      cost: ((.metrics.costMicros|tonumber)/1000000),
      conv: (.metrics.conversions|tonumber) }
' /tmp/gads_terms.ndjson \
| jq -s '
  [ .[] | . as $r | ($r.unigrams + $r.bigrams)[] | {gram:., cost:$r.cost, conv:$r.conv} ]
  | group_by(.gram)
  | map({ gram: .[0].gram, spend: (map(.cost)|add), conversions: (map(.conv)|add) })
  | map(select(.conversions == 0 and .spend > 25))
  | sort_by(-.spend)
'
```

> Search-term mining is the canonical safe audit. **WHITEHAT | 10/10** -- cutting wasted spend on irrelevant queries; pure account hygiene, zero policy exposure.

**Brand cannibalization %** -- share of conversions coming from brand campaigns (paying Google for demand you already own). Tag brand campaigns by naming convention:

```bash
gads_read /tmp/gads_brand.ndjson query "$CID" "
  SELECT campaign.name, metrics.conversions, metrics.cost_micros
  FROM campaign
  WHERE segments.date DURING LAST_30_DAYS AND campaign.status = 'ENABLED'
"
jq -s '
  map({ brand: (.campaign.name | test("(?i)brand")),
        conv: (.metrics.conversions|tonumber) })
  | { brand_conv:    (map(select(.brand))     | map(.conv)|add // 0),
      nonbrand_conv: (map(select(.brand|not)) | map(.conv)|add // 0) }
  | . + { brand_conv_pct:
            (if (.brand_conv + .nonbrand_conv) > 0
             then (.brand_conv / (.brand_conv + .nonbrand_conv) * 100) else 0 end) }
' /tmp/gads_brand.ndjson
```

> Bidding on your own brand to "protect" it is legitimate when a competitor is actually poaching the SERP. **GRAYHAT | 6/10** -- defensible defensively, but easily inflates reported conversions with traffic that would have converted organically; watch incrementality, not raw count. (Bidding on a *competitor's* trademarked brand in ad copy is a separate, riskier tactic -- **BLACKHAT | 3/10**, documented so you recognize it -- never deploy.)

### 5.4: Conversion-Action Health + Change-History Anomalies

Verify the conversion plumbing -- an ENABLED action with `all_conversions = 0` is a broken tag, not a quiet week:

```bash
gads_read /tmp/gads_convactions.ndjson query "$CID" "
  SELECT
    conversion_action.name,
    conversion_action.status,
    conversion_action.category,
    metrics.all_conversions
  FROM conversion_action
  WHERE segments.date DURING LAST_30_DAYS
"
```

Flag: `status != ENABLED` on a relied-on action; `all_conversions = 0` on an ENABLED action; a PRIMARY action with no recent volume. `all_conversions` (not `conversions`) is the right field -- it includes secondary/non-bidding actions.

> Verifying your own conversion plumbing. **WHITEHAT | 10/10** -- measurement integrity, no policy surface.

**Change-history anomaly scan** via the `change-status` convenience command (wraps `change_status`/`change_event`) -- detect mutations nobody on the team made:

```bash
gads_read /tmp/gads_changes.ndjson change-status "$CID"
jq -rc 'select(.changeStatus.lastChangeDateTime != null)
        | { when: .changeStatus.lastChangeDateTime,
            resource: .changeStatus.resourceType,
            status: .changeStatus.resourceStatus }' /tmp/gads_changes.ndjson
```

For actor + field granularity (who changed what, from which client), drop to raw GAQL on `change_event`:

```bash
gads_read /tmp/gads_changeevents.ndjson query "$CID" "
  SELECT
    change_event.change_date_time,
    change_event.user_email,
    change_event.client_type,
    change_event.change_resource_type,
    change_event.changed_fields
  FROM change_event
  WHERE change_event.change_date_time DURING LAST_14_DAYS
  ORDER BY change_event.change_date_time DESC
  LIMIT 200
"
```

Anomaly signals: budget or bidding-strategy edits you did not make; an unexpected `client_type` (e.g. `GOOGLE_ADS_RECOMMENDATIONS` auto-applying changes); edits from an unknown `user_email`. This is the tamper / auto-apply audit -- feed any unexpected mutation into the Phase 9 threshold alerts.

> Auditing who changed what. **WHITEHAT | 10/10** -- accountability and tamper detection.

### 5.5: Derived Metrics (micros converted)

- **CPA** = (cost_micros / 1e6) / conversions
- **ROAS** = conversions_value / (cost_micros / 1e6)
- **CTR** = clicks / impressions (CLI returns `ctr` directly; verify it matches)
- **Avg CPC** = average_cpc / 1e6 (returned in micros)

Populate the Google Ads row of the unified dashboard (Phase 7) and the `google_ads` snapshot block (Phase 8) from these results.

## Phase 6: Pull PostHog Analytics

If PostHog is configured:

### 6.1: Event Counts

Query PostHog for key events:
- Pageviews (with UTM filters for each paid channel)
- Signup events
- Purchase/upgrade events
- Custom conversion events

### 6.2: UTM-Filtered Funnels

For each paid channel, query the full funnel:
```
Ad Click -> Page View -> Signup -> Activation -> Purchase
```

Calculate step-by-step conversion rates per channel.

### 6.3: Cross-Channel Attribution

Compare each channel's reported conversions with PostHog's first-party data.

## Phase 7: Unified Dashboard

Combine all data sources into a single dashboard view:

```
GTM Unified Dashboard -- {date range}

REVENUE:  ${mrr}/mo MRR  |  {N} new customers  |  {X}% churn
SPEND:    ${total} across all channels
BLENDED:  ${cpa} CPA  |  {X}x ROAS

Cross-Channel Performance:
| Channel | Spend | Impressions | Clicks | Conv | CPA | Revenue | ROAS |
|---------|-------|-------------|--------|------|-----|---------|------|
| Meta Ads | ${X} | {N} | {N} | {N} | ${X} | ${X} | {X}x |
| Google Ads | ${X} | {N} | {N} | {N} | ${X} | ${X} | {X}x |
| Email | $0 | -- | {N} clicks | {N} | $0 | ${X} | -- |
| Organic/SEO | $0 | {N} | {N} | {N} | $0 | ${X} | -- |
| Direct | $0 | -- | -- | {N} | $0 | ${X} | -- |
| TOTAL | ${X} | {N} | {N} | {N} | ${X} | ${X} | {X}x |

> Google Ads row sourced from Phase 5: `spend` = account overview `cost_micros ÷ 1e6` (5.1), `impressions`/`clicks`/`conv` from the same roll-up, `revenue` = `conversions_value`, `CPA` = spend/conv, `ROAS` = revenue/spend. NEVER paste raw `cost_micros` into the Spend column -- convert first.

Cross-Channel Attribution:
| Metric | Meta Reports | Google Reports | PostHog (first-party) | Delta |
|--------|-------------|----------------|----------------------|-------|
| Conversions | {X} | {X} | {X} | {diff} |
| Revenue | ${X} | ${X} | ${X} (Stripe) | {diff} |

Top Performer: {channel} -- CPA ${X}, ROAS {X}x
Worst Performer: {channel} -- CPA ${X}, ROAS {X}x
```

### 7.1: Winner/Loser Analysis

Rank all ads/ad sets/emails by primary KPI. Identify:
- **Top 20%**: Scale these
- **Bottom 20%**: Kill or rotate these
- **Creative fatigue signals**: Frequency >3.0, declining CTR, rising CPA

### 7.2: Optimization Recommendations

Generate channel-specific and cross-channel recommendations:

**Budget Recommendations**:
- Shift budget toward highest-ROAS channel
- Kill underperforming campaigns/sequences

**Creative Recommendations**:
- Winning angles to scale
- Fatigued creatives to replace

**Channel-Specific**:
- Meta: targeting, placement, bid adjustments
- Email: subject line, send time, sequence length
- SEO: content updates, new keyword targets
- Outreach: reply rate improvements

## Phase 8: Save Metrics Snapshot

Save the unified metrics to `.gtm/metrics/snapshot-{YYYY-MM-DD}.json`:

```json
{
  "date": "{ISO date}",
  "period": "last_7d",
  "meta": { "spend": 0, "campaigns": [...] },
  "stripe": { "mrr": 0, "churn_rate": 0, "new_customers": 0, "ltv": 0 },
  "email": { "sent": 0, "opened": 0, "clicked": 0, "converted": 0 },
  "seo": { "organic_visitors": 0, "organic_conversions": 0 },
  "google_ads": {
    "spend": 0,
    "impressions": 0,
    "clicks": 0,
    "conversions": 0,
    "conv_value": 0,
    "cpa": 0,
    "roas": 0,
    "top_search_terms": [],
    "waste_ngrams": [],
    "brand_cannibalization_pct": 0
  },
  "posthog": { "meta_pageviews": 0, "meta_signups": 0, "funnel_rates": {} },
  "unified": {
    "total_spend": 0,
    "total_conversions": 0,
    "blended_cpa": 0,
    "total_revenue": 0,
    "blended_roas": 0
  },
  "attribution_comparison": {},
  "recommendations": []
}
```

The `google_ads` block is populated from Phase 5: `spend`/`cpa`/`roas`/`conv_value` are **dollars** (all `cost_micros` already ÷ 1e6 -- never store micros in the snapshot), `top_search_terms` is the 5.3 top-converters array (`[{term, conv, spend}]`), `waste_ngrams` is the 5.3 zero-conversion / spend>$25 n-gram array (`[{gram, spend, conversions}]`), and `brand_cannibalization_pct` is the 5.3 brand-share figure.

## Phase 9: Threshold Check (Auto Mode)

If `--auto` flag is present, check these thresholds against 7-day averages:

| Metric | Threshold | Action |
|--------|-----------|--------|
| CPA increase | >30% vs. 7d avg | ALERT |
| CTR decrease | >25% vs. 7d avg | ALERT |
| Daily spend | >20% over budget | ALERT |
| Email bounce rate | >5% | ALERT |
| Churn rate | >2x monthly avg | ALERT |
| Campaign auto-paused | Any | ALERT |

### 9.1: Google Ads-Specific Thresholds

| Metric | Threshold | Source | Action |
|--------|-----------|--------|--------|
| Search impression share drop | absolute SIS <X% OR >10pp drop vs. 7d avg | GAQL: `metrics.search_impression_share`, `metrics.search_budget_lost_impression_share`, `metrics.search_rank_lost_impression_share` FROM `campaign` | ALERT -- flag whether loss is budget vs. rank |
| Conversion action stopped receiving conversions | ENABLED action with `all_conversions = 0` in the period (5.4) | `conversion_action` health pull | ALERT -- likely broken tag, not a slow week |
| Unexpected change-status mutation | Any budget/bidding/status edit from an unknown `user_email` or `client_type = GOOGLE_ADS_RECOMMENDATIONS` you did not authorize (5.4) | `change-status` / `change_event` scan | ALERT -- tamper / auto-apply |

Search impression share pull (note: SIS comes back as a 0-1 ratio, not micros; multiply by 100 for percent):

```bash
gads_read /tmp/gads_sis.ndjson query "$CID" "
  SELECT
    campaign.name,
    metrics.search_impression_share,
    metrics.search_budget_lost_impression_share,
    metrics.search_rank_lost_impression_share
  FROM campaign
  WHERE segments.date DURING LAST_7_DAYS AND campaign.status = 'ENABLED'
"
```

A budget-lost SIS means raise budget; a rank-lost SIS means raise bids or improve Quality Score. The conversion-action and change-status alerts reuse the Phase 5.4 pulls -- do not re-query.

Save alerts to `.gtm/routines/alerts/alert-{YYYY-MM-DD}.json`.

## Output

```
GTM Metrics Dashboard -- {date range}

{Unified dashboard from Phase 7}

Snapshot saved: .gtm/metrics/snapshot-{date}.json
{Alerts if any}

Next: Run /gtm-learn to save insights, or /gtm-report for a full weekly report.
```

## Error Handling

- **Meta token expired**: Detect error code 190, prompt for new token, STOP.
- **Meta rate limiting**: Wait and retry with backoff (30s, 60s, 120s).
- **Google Ads auth expired**: `gads_read` returns normalized `3` (stderr matches `/auth|token|credential|unauthenticated|permission/i`). Tell operator to re-run `google-ads-open-cli auth login` (or refresh `GOOGLE_ADS_ACCESS_TOKEN` in CI). In `--auto`, exit 3; interactive, prompt.
- **Google Ads API error**: `gads_read` returns normalized `4`. Backoff 30s and retry once, then alert. Do NOT treat as auth.
- **Google Ads CLI missing**: `command -v google-ads-open-cli` empty -> note "run `npm install -g google-ads-open-cli`", skip channel.
- **Stripe unavailable**: Continue without revenue data. Note: "Stripe data unavailable."
- **Email provider unavailable**: Continue without email data. Note gap.
- **PostHog unavailable**: Continue with channel-native data only. Note: "PostHog data unavailable -- cross-attribution skipped."
- **No campaign data**: Report: "No active campaigns with spend found."
- **Auto mode errors**: Log errors but do not stop. Report partial data with gaps noted.
