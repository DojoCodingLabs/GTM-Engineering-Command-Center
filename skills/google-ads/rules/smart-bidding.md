# Google Ads Smart Bidding -- Migration Ladder, Value Signals, and Pipeline Truth

Modern Search lives and dies on automated bidding. The craft is managing the **signals** you feed the algorithm, not the bids themselves. Distilled from Atlas Part IV (+ Part XI pipeline value bidding, + Part XV under-bidding).

**Execution is hybrid.** Reading current bid strategy, conversion volume, and stats is READ-ONLY via `google-ads-open-cli` (see `skills/google-ads/rules/gads-cli.md`). Changing a bid strategy, target, or budget is a WRITE via the Google Ads REST API `:mutate` endpoint with curl — no first-party CLI mutates. Every step below is labeled READ or WRITE.

**Money is in micros.** `1,000,000 micros = $1`. `targetCpaMicros`, `cpcBidCeilingMicros`, budget `amountMicros` are all micros. tROAS (`targetRoas`) is a raw multiplier (`4.0` = 400%), NOT micros. Every `cost_micros` the read CLI returns must be `÷ 1e6` for dollars. This is the Google analog of Meta's "cents" gotcha — get it wrong and you set a $4 tCPA as $4,000,000.

**All bid-strategy writes default to `status: PAUSED`** on the campaign until verified.

---

## The Migration Ladder

The settled doctrine for moving a campaign up the automation stack. Do **not** skip rungs — each rung exists to seed the signal the next rung consumes.

| Rung | Strategy | Move up when | API field |
| :---- | :---- | :---- | :---- |
| 1. Launch | Manual CPC | Seed core match + click signals; live immediately | `manualCpc` |
| 2. Traffic | Maximize Clicks (get off ASAP) | Base click/CTR data exists | `targetSpend` |
| 3. Conversions | Maximize Conversions → Target CPA | ~30 conv/mo/campaign | `maximizeConversions` → `targetCpa` |
| 4. Value | Maximize Conversion Value → Target ROAS | ~60 days value data **and** ≥2 distinct conversion values | `maximizeConversionValue` → `targetRoas` |

Rules of the ladder:

- **Maximize Clicks is a transit station, not a home.** It optimizes for clicks, not buyers. Get off as fast as base data allows.
- **~30 conv/mo/campaign is the tCPA gate.** Below that, Smart Bidding starves and bids erratically.
- **tROAS needs both ~60 days of value data AND ≥2 distinct conversion values.** One flat value gives the algorithm nothing to optimize ratio against.
- **Below ~30 conv/mo: no tROAS, no aggressive broad match.** Consolidate ad groups/campaigns to pool conversion density instead.
- **Navah Hopkins:** accounts under ~$5,000/mo often should not be on Smart Bidding at all yet. The community feeder logic echoes this — pool data before you automate it.

```bash
# READ: where does this campaign sit on the ladder right now?
google-ads-open-cli campaign <id> <campaign_id> --format compact
# READ: is it past the ~30 conv/mo tCPA gate? (cost_micros ÷ 1e6 for $)
google-ads-open-cli campaign-stats <id> --campaign <campaign_id> \
  --start 2026-05-15 --end 2026-06-14
```

```bash
# WRITE: rung 3 — migrate a qualifying campaign to Target CPA (PAUSED first).
# targetCpaMicros = $50 tCPA = 50 * 1e6 = 50000000 micros
curl -X POST \
  "https://googleads.googleapis.com/v18/customers/<id>/campaigns:mutate" \
  -H "Authorization: Bearer $GOOGLE_ADS_ACCESS_TOKEN" \
  -H "developer-token: $GOOGLE_ADS_DEVELOPER_TOKEN" \
  -H "login-customer-id: $GOOGLE_ADS_LOGIN_CUSTOMER_ID" \
  -H "Content-Type: application/json" \
  -d '{"operations":[{"update":{
        "resourceName":"customers/<id>/campaigns/<campaign_id>",
        "status":"PAUSED",
        "maximizeConversions":{"targetCpaMicros":"50000000"}
      },"updateMask":"status,maximize_conversions.target_cpa_micros"}]}'
```

---

## The 70-80% Target Rule

Setting aggressive automated targets too early throttles delivery — the algorithm refuses auctions it thinks it can't win at your number, and learning stalls.

The guardrail (associated with agency practice such as Tegra):

1. Set the **initial tCPA or tROAS at 70-80% of trailing actual performance**. Looser than reality, so delivery stays open.
2. Give it **~2 weeks to stabilize** (do not touch it mid-cycle — every edit re-enters learning).
3. **Tighten in ~10% steps**, one step at a time, re-stabilizing between.
4. Set a **tROAS at the profitable floor, not the historical average.** The average includes deals you'd happily lose money on; the floor is where the next marginal deal still pays.

```bash
# READ: trailing actual to anchor the 70-80% target.
# Actual CPA = (sum cost_micros ÷ 1e6) ÷ conversions over trailing window.
google-ads-open-cli campaign-stats <id> --campaign <campaign_id> \
  --start 2026-05-15 --end 2026-06-14 --format compact
# e.g. cost_micros 4,200,000,000 = $4,200 ; conversions 70 → actual CPA $60.
# Initial tCPA = 70-80% looser = ~$72-86 (target ABOVE actual to open delivery),
# then tighten toward $60 floor in 10% steps over successive 2-week holds.
```

**WHITEHAT | 10/10** — A standard pacing tactic to prevent algorithmic throttling.

---

## Value-Based Bidding for Low-Volume & High-Ticket

High-ticket info products (five-figure coaching cohorts) and enterprise SaaS often produce **fewer than 10 closed deals per month** — far below the volume Smart Bidding needs. The fix is a **tiered micro-conversion value ladder**: assign calculated values to upstream actions so the campaign keeps the conversion *density* to bid on, while still steering toward real revenue.

| Funnel stage | Illustrative assigned value |
| :---- | :---- |
| Free trial activated | $50 |
| Product demo requested | $500 |
| Qualified lead / SQL | $900 to $2,000 |
| Sales opportunity created | $3,000 |
| Closed-won revenue | Actual value, e.g. $15,000 |

Without tiered values, the algorithm treats a $5k trial signup and a $500k enterprise opportunity as **equally valuable**. You need **≥2 unique conversion values and several complete conversion cycles** before tROAS is stable.

**Firebrand's warning** — heed it: offline conversion tracking plus value bidding can quietly **wreck a campaign** if (a) the click-to-deal lag exceeds the bidding lookback window, or (b) you over-optimize to a rare deep event. Keep the data flowing for *insight* even when you do not let it *drive bidding* — measure the deep event, bid on a denser upstream one.

```bash
# READ: confirm ≥2 distinct conversion values exist before going tROAS.
google-ads-open-cli conversion-actions <id> --format compact
# READ: confirm closed-won lag is INSIDE the lookback (else value bidding mis-attributes).
google-ads-open-cli query <id> \
  "SELECT conversion_action.name, metrics.conversions, metrics.conversions_value \
   FROM conversion_action WHERE segments.date DURING LAST_30_DAYS"
```

Set the values via conversion-action default values or per-event uploads (WRITE — see `skills/google-ads/rules/conversion-tracking.md` for the offline-import `:mutate` flow). Feed CRM stage values, not guesses.

**WHITEHAT | 10/10** — Feeding factual revenue and stage values back to Google is best practice and the most consistent anti-spam lever (value-based bidding sourced from the CRM).
**GRAYHAT | 4/10** — Assigning uniform static values to leads of genuinely different quality skews returns and teaches the engine the wrong economics; manipulating reported values purely to game bidding distorts signals and risks policy issues if deceptive.
**BLACKHAT | 2/10** — *Documented so you recognize it — never deploy.* Generating false conversion/pixel events (bot clicks, fake test leads) to inflate volume and manipulate Smart Bidding violates policy and can trigger suspension.

---

## Bid to Pipeline Truth, Not Form-Fill Vanity

(Atlas Part XI) The feedback loop of doom: **without CRM data, PMax and Smart Bidding optimize to the cheapest form fills** — which are rarely qualified. The cure is to bid to the *right event*, deep in the pipeline.

**The math.** If form-fill CPA is **$150** and **MQL→SQL is 15%**, the true cost per SQL is `$150 ÷ 0.15 ≈ $1,000`.

- Set **tCPA at cost-per-SQL ($1,000), not cost-per-form-fill ($150)**.
- Then **migrate from tCPA toward value-based tROAS tied to CRM stages**, so the engine prioritizes high-value enterprise deals over low-fit signups.

```
Form fill CPA          $150   ← what the pixel sees (vanity)
× (1 / MQL→SQL 15%)
= Cost per SQL       ~$1,000   ← what you actually bid to (truth)
→ then tROAS on CRM-stage values  ← what you graduate to
```

**For info products — bid to a bridge, then graduate.** Start bidding to a bridge conversion (webinar registration), then **graduate** the primary conversion up the chain: show-up → application/approval → booked call → purchase. **Do not make all the soft conversions primary at once** — that teaches the system to go find cheap clickers who register and vanish.

```
Stage 1 primary: Webinar registration   (dense — seeds the algorithm)
Stage 2 primary: Show-up / booked call   (graduate once volume holds)
Stage 3 primary: Purchase                (final — once it's the densest reliable event)
```

```bash
# READ: which conversion actions are flagged primary today? Graduate one at a time.
google-ads-open-cli query <id> \
  "SELECT conversion_action.name, conversion_action.primary_for_goal \
   FROM conversion_action WHERE conversion_action.status = 'ENABLED'"
```

**WHITEHAT | 9/10** — Bidding to SQL/revenue stage instead of form-fill or registration alone correlates with LTV and payback; graduating soft conversions one rung at a time avoids training the engine on cheap clickers.

---

## The 2026 AI Bidding Stack

Google is pushing the bidding layer hard. Know what's real and what's marketing.

| Feature | What it is | Operator read |
| :---- | :---- | :---- |
| **Smart Bidding Exploration** | Positioned as the "biggest bidding update in over a decade"; by GML 2026 expanding toward PMax + Shopping | Real lever, worth testing. Google's **"27% more unique converting users"** is a *Google figure — treat as marketing*, not a forecast for your account. |
| **Journey-aware bidding** | Designed to learn from the **full customer journey**, not only the last biddable conversion | Potentially meaningful for **long-cycle SaaS and high-ticket info products**; independent public evidence remains **thin**. Pilot, measure incrementally, don't bet the budget. |

Test these *after* signal hygiene (conversion tracking + CRM loop) is in place — automation amplifies whatever signal you give it, good or garbage.

---

## Contrarian: Deliberate Under-Bidding to Seed Data

(Atlas Part XV) **SavvyRevenue:** if your real target is, say, **300% ROAS**, you may deliberately set a **100% tROAS goal at a temporary loss** — because the looser goal feeds the algorithm the *right kind of data*, letting it explore auctions it would otherwise skip. Once the model has learned the converting surface, you tighten back toward the real target.

This is the same principle as the 70-80% rule, pushed further: in a low-volume account, a temporary low target (or capped Max-Clicks) **starves premature Smart Bidding of the chance to over-optimize on too little data**, then graduates it once density exists. Pair with **portfolio tCPA + max-bid caps** (`cpcBidCeilingMicros`) so you don't overpay outlier auctions during the exploration window.

```bash
# READ: is volume thin enough that under-bidding to explore makes sense?
google-ads-open-cli campaign-stats <id> --campaign <campaign_id> \
  --start 2026-05-15 --end 2026-06-14 --format compact
# <~30 conv/mo → under-bid/seed; ≥~30 → tighten toward the real target instead.
```

**GRAYHAT | 7/10** — Deliberate under-bidding (and Max-Clicks/capped tactics) to seed the learning system at a short-term loss is useful in low-volume accounts and **exploits the learning system** — allowed, but watch it: leave it on too long and you train the engine toward cheap, low-value conversions.
