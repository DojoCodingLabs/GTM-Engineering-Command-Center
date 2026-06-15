# Performance Max -- Control, Feeders, and Anti-Spam

Source: Atlas Part III (PMax control + Moran feeder), Part XII (Mike Rhodes script). PMax buys all Google inventory at once and is opaque by design. The 2025-2026 reality: Google handed back real levers. The craft is wrestling control back from the automation.

Execution is hybrid. **READ/MEASURE/AUDIT** -> `google-ads-open-cli` (read-only Node CLI; see `skills/google-ads/rules/gads-cli.md`). **WRITE/DEPLOY** -> Google Ads REST API `:mutate` via `curl` (no first-party CLI mutates). Every step below names its path. All campaign writes default to **status PAUSED**.

**Money is in micros: 1,000,000 micros = $1.** Budgets are `amountMicros`; all `cost_micros` from stats divide by 1e6 for dollars. This is the Google analog of Meta's "cents" gotcha -- a tROAS budget typed in dollars is off by a million.

---

## The Control Levers That Now Exist (2026)

The PMax control surface as of 2026:

| Lever | What it does | Cap / note |
|---|---|---|
| Channel-level reporting | See Search vs YouTube vs Display vs Discover spend split | Read via GAQL `segments.ad_network_type` |
| Full search-terms insights | Actual queries, not just categories | Degrading like Search SQR -- mine n-grams |
| Campaign-level negative keyword lists | Block queries at the campaign | Raised 100 -> **10,000 in March 2025** |
| Account-level negatives | Universal junk block | Cap **1,000** |
| Brand exclusions | Entity-based strip of Search/Shopping brand traffic | Catches misspellings, variants, languages |
| Customer-list exclusions | **Real exclusions, not signals** -- the list is actually suppressed | Match-rate dependent |
| Demographic + device controls | Exclude age/gender/income bands, device classes | Bid-modifier-grade control |
| Budget pacing reports | MTD spend vs target | Align script timezone to account (Part XII) |

**READ — channel split (where is the money actually going):**
```bash
google-ads-open-cli query <CID> \
  "SELECT campaign.name, segments.ad_network_type, metrics.cost_micros, metrics.conversions \
   FROM campaign WHERE campaign.advertising_channel_type = 'PERFORMANCE_MAX' \
   AND segments.date DURING LAST_30_DAYS" --format compact
```
`cost_micros / 1e6` for dollars. If YouTube/Display dominate a lead-gen PMax, you are funding the spam surface (see below).

If the CLI exits non-zero: capture stderr. Matches `/auth|token|credential|unauthenticated|permission/i` -> auth error, tell operator to re-run `google-ads-open-cli auth login`. Otherwise -> API error, backoff + one retry.

---

## Brand Exclusions vs Negatives vs Restrictions

Three different tools, three different surfaces. Pick by what you need to strip.

| Tool | Strips | Use when |
|---|---|---|
| **Brand Exclusions** (entity-based) | Search + Shopping brand traffic | You want PMax off your brand on the text/shopping side; catches misspellings, variants, other languages automatically |
| **Negative keyword lists** | Adds Video + Display brand traffic on top | Brand creative is leaking through YouTube/Display, not just Search |
| **Brand Restrictions** | Inverts -- builds a **brand-only** PMax | You deliberately want a brand-defense PMax that only serves on brand |
| **Account-level negatives** | Universal junk across the account | Reserve for `free`, `jobs`, `salary`, `login`, `careers` -- never burn the 1,000 cap on campaign-specific terms |

Default play: Brand Exclusions to keep automated PMax from backfilling cheap brand demand your branded Search campaign should own at a lower CPC. Layer a negative keyword list only when Video/Display brand impressions still leak.

**READ — confirm brand list is applied:**
```bash
google-ads-open-cli negative-keywords <CID>
google-ads-open-cli query <CID> \
  "SELECT campaign.name, campaign.brand_guidelines_enabled FROM campaign \
   WHERE campaign.advertising_channel_type = 'PERFORMANCE_MAX'"
```

**WRITE — attach a shared negative keyword list to a PMax campaign (`:mutate`):**
```bash
curl -s -X POST \
  "https://googleads.googleapis.com/v18/customers/<CID>/campaignSharedSets:mutate" \
  -H "Authorization: Bearer ${GOOGLE_ADS_ACCESS_TOKEN}" \
  -H "developer-token: ${GOOGLE_ADS_DEVELOPER_TOKEN}" \
  -H "login-customer-id: ${GOOGLE_ADS_LOGIN_CUSTOMER_ID}" \
  -H "Content-Type: application/json" \
  -d '{"operations":[{"create":{
        "campaign":"customers/<CID>/campaigns/<CAMPAIGN_ID>",
        "sharedSet":"customers/<CID>/sharedSets/<SHARED_SET_ID>"}}]}'
```
Brand Exclusions themselves attach via the campaign's `brand_guidelines` / brand list resources -- read the current state first, mutate the campaign to reference the brand list.

**WHITEHAT | 9/10** — Aggressive brand exclusions and negatives keep automated campaigns from backfilling easy brand demand you already own cheaper. Native, intended configuration.

---

## Feed-Only & Limited-Asset Setups

For physical tripwire goods, starve the asset group so PMax behaves like Shopping on high-intent placements:

```
Asset group config for feed-only behavior:
  - NO headlines
  - NO descriptions
  - NO images
  - NO video
  - Final URL Expansion: OFF
  - Automatically Created Assets: OFF
  -> PMax falls back to the Merchant Center feed -> Shopping-like delivery
```

**Caveat:** Merchant Center typically allows only **one** such asset group. Adding more in Google Ads trips the **three-headline minimum**, which breaks feed-only. One feed-only asset group per campaign is the ceiling.

**READ — verify the asset group is genuinely asset-starved:**
```bash
google-ads-open-cli assets <CID> --type TEXT
google-ads-open-cli query <CID> \
  "SELECT asset_group.name, asset_group_asset.field_type, asset.type \
   FROM asset_group_asset WHERE asset_group.name = '<NAME>'"
```
If text/image/video assets show up, the build is not feed-only -- it will expand off-feed.

**WRITE:** asset-group asset removal and `final_url_expansion_opt_out` / automated-asset settings go through `assetGroupAssets:mutate` (remove ops) and `campaigns:mutate` on the URL-expansion field. Default PAUSED until the feed link is confirmed.

**WHITEHAT | 9/10** — Feed-only and limited-asset setups use Google's native asset rules to restrict placements; fully within the allowed configuration.

---

## Asset-Group-as-Persona

Tempting model: treat each asset group like a paid-social ad set -- one persona, its own audience signal, search themes, and creative. The Optmyzr data complicates it.

```
The naive structure:                 What the data prefers:
  ONE PMax campaign                    MULTIPLE PMax campaigns
    ├─ Asset group: Persona A            ├─ Campaign A -> single asset group
    ├─ Asset group: Persona B            ├─ Campaign B -> single asset group
    └─ Asset group: Persona C            └─ Campaign C -> single asset group
  (often fragments the data)          (often the best ROAS, per Optmyzr)
```

- Multiple campaigns each with a **single** asset group frequently outperformed cluttered multi-persona structures.
- **Lead gen has no Listing Groups tab** -> you cannot segment by product; segment by **campaign** instead.
- Segment only when personas genuinely need **different creative and different URLs**. Otherwise you are splitting conversion data below the volume PMax needs to learn.

**READ — check whether segmentation is helping or just thinning data:**
```bash
google-ads-open-cli campaign-stats <CID> --start 2026-05-01 --end 2026-05-31 \
  --segments ad_network_type
google-ads-open-cli query <CID> \
  "SELECT asset_group.name, metrics.conversions, metrics.cost_micros \
   FROM asset_group WHERE segments.date DURING LAST_30_DAYS"
```
If a persona asset group is under-converting (see the ~60-conversion floor below), collapse it.

**WHITEHAT | 8/10** — Persona asset groups help when segmentation matches real demand and hurt when they just fragment data.

---

## The Lead-Gen Spam Problem & How to Kill It

**Atlas Law 3: guilty until proven innocent.** PMax for lead gen gets spammed hard. The primary source is its reach on **YouTube and mobile app inventory**, flagged by referral params like `mobile.yt` or `mobile.youtube.com` in click logs. Left to optimize a cheap event, PMax is simultaneously great at volume and great at finding the lowest-quality leads it possibly can (Laura Schiele, Search Engine Land).

The fixes that work, in order of leverage:

1. **Optimize to a deeper, human-only action.** Bid to **qualified lead / purchase / webinar-attended** via Enhanced Conversions + offline import -- never the raw form fill. **This is the single most consistent anti-spam lever in PMax and Search.** Bots can fill a form; they cannot show up to a webinar or pass SQL review.
2. **Strip video assets.** Removing video from a lead-gen PMax avoids most YouTube and `mobile.yt` spam routing.
3. **Harden the form.** Replace single-field email capture with **multi-step qualification** (company size, current stack, specific pain) so bot auto-fill templates fail. Layer **reCAPTCHA v3** + hidden **honeypot** fields that filter bot submissions before the conversion fires.
4. **Cap custom conversions early + prune placements.** Keep to **1-2 custom conversions** in the learning window; review placement reports and exclude low-value mobile app inventory.

**READ — find the spam source in click logs:**
```bash
google-ads-open-cli query <CID> \
  "SELECT campaign.name, segments.ad_network_type, metrics.conversions, metrics.cost_micros \
   FROM campaign WHERE campaign.advertising_channel_type = 'PERFORMANCE_MAX' \
   AND segments.ad_network_type = 'YOUTUBE_WATCH' AND segments.date DURING LAST_30_DAYS"
```
High YouTube/mobile-app conversions with near-zero downstream qualified value = the spam pattern. Strip video, re-point optimization deeper.

**WRITE:** placement exclusions via the placement exclusion list `:mutate`; conversion-goal re-pointing via `customers/<CID>/conversionActions` + campaign goal `:mutate`. Honeypot/reCAPTCHA live on the landing page, not the API.

**WHITEHAT | 10/10** — Honeypots and reCAPTCHA are standard security to filter fraudulent bot activity.

**GRAYHAT | 5/10** — Removing video specifically to game spam routing is intentional signal manipulation, allowed but not what Google intends. Defensible (you are buying out of a fraud-heavy surface), still deliberate.

---

## The John Moran Feeder Strategy

Associated with John Moran (Solutions 8 / Tier 11), one of the most-discussed beyond-the-docs playbooks. Two campaigns cooperate: a cheap **feeder** that warms first-party audiences, and a **converter** that closes them.

```
ECOMMERCE FORM (the original):
  FEEDER:    Standard Shopping, low tROAS (~400%) or Maximize Clicks
             -> captures cold high-intent traffic
             -> populates first-party remarketing pools
  CONVERTER: feed-only PMax, higher tROAS (~500%)
             -> converts the warmed audiences

LEAD-GEN ADAPTATION:
  FEEDER:    low-friction, high-intent Search campaign
             -> verified leads only into the remarketing pool
  CONVERTER: no-video PMax remarketing campaign
             -> fed ONLY by verified leads (kills the spam vector by construction)
```

Moran also detailed (Perpetual Traffic) deliberately setting **higher tROAS targets to push ad rank, and therefore CPC, down on purpose** -- forcing cheaper clicks while PMax acts as the second-click conversion layer.

> **Honesty caveat on the numbers.** The widely cited results are **ecommerce, not lead gen**. GrowMyAds: revenue +108% (~$37k/mo added, $50k -> $100k+ baseline) on 54% more spend, conversions +106%, ROAS 5.8x -> ~8.0x in 22 days. A single-product Google Ads Aficionados test: +127.81% revenue. **These are Shopping + PMax ecommerce cases.** The lead-gen spam-reduction benefit is described qualitatively, not cleanly quantified in public; one circulating lead-gen figure (~215% more spend, 84% CPA drop, 63% higher ROAS) is loosely sourced. **Treat the structure as strong and real; treat the headline percentages as ecommerce evidence.**

**WRITE — set the feeder's deliberately-high tROAS (the push-ad-rank-down maneuver, micros-aware):**
```bash
# tROAS is a ratio, NOT micros. Budget below IS micros: $50/day = 50000000.
curl -s -X POST \
  "https://googleads.googleapis.com/v18/customers/<CID>/campaigns:mutate" \
  -H "Authorization: Bearer ${GOOGLE_ADS_ACCESS_TOKEN}" \
  -H "developer-token: ${GOOGLE_ADS_DEVELOPER_TOKEN}" \
  -H "login-customer-id: ${GOOGLE_ADS_LOGIN_CUSTOMER_ID}" \
  -H "Content-Type: application/json" \
  -d '{"operations":[{"update":{
        "resourceName":"customers/<CID>/campaigns/<CONVERTER_ID>",
        "maximizeConversionValue":{"targetRoas":5.0},
        "status":"PAUSED"},
        "updateMask":"maximize_conversion_value.target_roas,status"}]}'
```
`targetRoas: 5.0` = 500%. Confirm budget separately with `campaign-budgets <CID>` (read) -- `amountMicros` is dollars x 1e6.

**GRAYHAT | 7/10** — The deliberate push-ad-rank-down maneuver exploits auction mechanics in an unintended way; no policy violation and sustainable. The coordination of Shopping/Search and PMax bidding itself is whitehat.

---

## What the Optmyzr Data Shows

Optmyzr's **9,199-account** PMax study -- the most useful neutral evidence on where real advertisers actually land:

| Finding | Implication |
|---|---|
| **82%** ran PMax alongside other campaign types | PMax is a layer, not a replacement -- keep Search running |
| Multiple campaigns w/ a **single asset group** -> best ROAS | Confirms the structure above; resist persona sprawl |
| Accounts under **~60 conversions** underperform across most metrics | Below the floor, PMax cannot learn -- consolidate or wait |
| **Video is the closest thing to a PMax magic button** | Text-only success is largely confined to Search; add video everywhere except the lead-gen anti-spam build |

Kirk Williams (ZATO) adds the consistent practitioner read: smaller accounts struggle with PMax; larger, data-rich accounts do well. The ~60-conversion floor is the line.

**READ — check the conversion floor before trusting PMax results:**
```bash
google-ads-open-cli campaign-stats <CID> --start 2026-04-01 --end 2026-04-30 --campaign <PMAX_ID>
```
If 30-day `conversions` < ~60, the account is below the learning floor -- the data is noise, not signal.

---

## The Mike Rhodes PMax Script

Roughly **3,200 lines**, free version on GitHub + a paid tier (Atlas Part XII). Used inside agencies from Dentsu to Publicis and by brands including Thinkific. It surfaces everything PMax hides:

- **Splits PMax channel spend** -- Search vs YouTube vs Display, the report Google buried.
- **Buckets search categories** -- brand / close-to-brand / non-brand.
- **Buckets products** -- zombies (no impressions) / zero-conversion / profitable.
- **Surfaces placements** -- the mobile-app and YouTube junk you exclude.
- **Audits assets** -- coverage and performance gaps per asset group.

This is the read/audit complement to the CLI: the script runs inside Google Ads as a scheduled Apps Script (it reads, reports to a Sheet, and emails), while `google-ads-open-cli` is your ad-hoc terminal read path. Neither mutates -- all fixes the script surfaces get deployed via the `:mutate` curl patterns above (placement exclusions, brand lists, asset removals), defaulting to PAUSED.

**WHITEHAT | 10/10** — Scripts for channel splits, n-grams, placement audits, and asset coverage fill blind spots the native UI leaves. Pure visibility, zero policy surface.

---

## Quick Reference: Read vs Write Path

| Task | Path | Command surface |
|---|---|---|
| See PMax channel split | READ | `query <CID>` w/ `segments.ad_network_type` |
| Find spam (YouTube/mobile.yt) | READ | `query` filter `ad_network_type='YOUTUBE_WATCH'` |
| Check conversion floor (~60) | READ | `campaign-stats <CID> --campaign <PMAX_ID>` |
| Audit asset-group coverage | READ | `assets <CID> --type` / Rhodes script |
| Attach negative keyword list | WRITE | `campaignSharedSets:mutate` |
| Set feeder/converter tROAS | WRITE | `campaigns:mutate` (ratio, not micros) |
| Exclude junk placements | WRITE | placement exclusion list `:mutate` |
| Remove assets (feed-only) | WRITE | `assetGroupAssets:mutate` |

All writes default to **status PAUSED**. All money fields are **micros** unless they are a ratio (tROAS) or percentage. CLI reference: `skills/google-ads/rules/gads-cli.md`.
