# Meta Ads CLI — Plugin Reference

The official Meta `meta ads` CLI shipped April 29, 2026. The plugin uses it as the primary tool for all vanilla Meta Marketing API operations. Raw Graph API is reserved for the patterns the CLI does not yet support (listed at the bottom).

**Official docs:** https://developers.facebook.com/documentation/ads-commerce/ads-ai-connectors/ads-cli/

---

## 1. Install

```bash
# Preferred — isolated tool install via uv
uv tool install meta-ads

# Or pip
pip install meta-ads
```

Package name on PyPI is **`meta-ads`** (NOT `meta-ads-cli` — that's an unrelated third-party package). Requires Python 3.12+.

Verify install:
```bash
meta --version
meta auth status
```

---

## 2. Auth + Configuration

### Environment variables

| Var | Required | Purpose |
|---|---|---|
| `ACCESS_TOKEN` | yes | System User access token from Meta Business Suite |
| `AD_ACCOUNT_ID` | yes (most commands) | Format: `act_XXXXX` |
| `BUSINESS_ID` | optional | For catalog/dataset commands |

### `.env.gtm` (gitignored — preferred)

```bash
ACCESS_TOKEN='<system-user-token>'
AD_ACCOUNT_ID='act_XXXXX'
BUSINESS_ID='<business-id>'
```

The plugin's setup wizard writes this file when Meta credentials are configured.

### Required token scopes

```
business_management
ads_management
pages_show_list
pages_read_engagement
pages_manage_ads
catalog_management
read_insights
```

### Resolution order (highest priority first)

1. CLI flags (`--ad-account-id`)
2. Environment variables
3. Project `.env` / `.env.gtm`
4. User config: `~/.config/meta/`

---

## 3. Global Flags

Place before the subcommand:

```bash
meta [global options] ads <command> <subcommand> [options]
```

| Flag | Short | Purpose |
|---|---|---|
| `--output {table,json,plain}` | `-o` | Output format. **Plugin agents always use `json`.** |
| `--no-color` | | Disable ANSI |
| `--no-input` | | CI mode — disable interactive prompts |
| `--debug` | | Verbose error output |
| `--version` | `-v` | |
| `--help` | `-h` | |

---

## 4. Command Catalog

```
meta auth status
meta auth login

meta ads adaccount list | get
meta ads page list

meta ads campaign list | get | create | update
meta ads adset    list | get | create | update
meta ads ad       list | get | create | update
meta ads creative list | get | create | update

meta ads dataset  list | get | create | connect | disconnect | assign-user
meta ads catalog  list | get | create | update

meta ads insights get
```

Pattern: `meta ads <resource> <action> [options]`. Output is always JSON-pipeable when `--output json` is set.

---

## 5. Plugin Defaults — Free with the CLI

These are now enforced by the tool itself (no agent vigilance needed):

| Plugin "Critical Rule" | CLI default |
|---|---|
| Always create as PAUSED | `--status` defaults to `PAUSED` |
| Budget in cents | All `--*-budget` flags accept cents |
| Image upload via adimages, never URL | `--image`/`--images` auto-uploads from local file |
| Provide both 1:1 and 9:16 images | `--images` accepts repeated paths up to 10 |

Agents no longer need to manually verify these — the CLI rejects invalid input.

---

## 6. Deploy Flow (4 calls)

The plugin's pre-CLI deploy was 7 steps (5 pre-flight + image upload + campaign + adset + creative + ad + verify). With the CLI it collapses to 4 creation calls because image upload is implicit.

### Step 1: Campaign

```bash
CAMPAIGN_ID=$(meta ads campaign create \
  --name "$CAMPAIGN_NAME" \
  --objective OUTCOME_LEADS \
  --status PAUSED \
  --output json | jq -r '.id')
```

### Step 2: Ad set

```bash
ADSET_ID=$(meta ads adset create "$CAMPAIGN_ID" \
  --name "$ADSET_NAME" \
  --daily-budget 5000 \
  --optimization-goal OFFSITE_CONVERSIONS \
  --billing-event IMPRESSIONS \
  --pixel-id "$PIXEL_ID" \
  --custom-event-type LEAD \
  --start-time "2026-05-01T00:00:00Z" \
  --targeting-countries US \
  --status PAUSED \
  --output json | jq -r '.id')
```

`--custom-event-type` values: `ADD_PAYMENT_INFO, ADD_TO_CART, ADD_TO_WISHLIST, COMPLETE_REGISTRATION, CONTACT, CUSTOMIZE_PRODUCT, DONATE, FIND_LOCATION, INITIATED_CHECKOUT, LEAD, PURCHASE, SCHEDULE, SEARCH, START_TRIAL, SUBMIT_APPLICATION, SUBSCRIBE, VIEW_CONTENT`.

### Step 3: Creative (with DCO)

```bash
CREATIVE_ID=$(meta ads creative create \
  --name "$CREATIVE_NAME" \
  --page-id "$PAGE_ID" \
  --instagram-actor-id "$INSTAGRAM_ACTOR_ID" \
  --link-url "https://example.com/?utm_source=meta&utm_medium=paid&utm_campaign=$CAMPAIGN_NAME" \
  --images "./creatives/$CAMPAIGN/feed-1080x1080.png" \
  --images "./creatives/$CAMPAIGN/story-1080x1920.png" \
  --titles "Headline 1" --titles "Headline 2" --titles "Headline 3" --titles "Headline 4" --titles "Headline 5" \
  --bodies "Body 1" --bodies "Body 2" --bodies "Body 3" --bodies "Body 4" --bodies "Body 5" \
  --descriptions "Desc 1" --descriptions "Desc 2" --descriptions "Desc 3" --descriptions "Desc 4" --descriptions "Desc 5" \
  --call-to-actions SIGN_UP \
  --output json | jq -r '.id')
```

DCO limits: **10 images, 10 videos, 5 titles, 5 bodies, 5 descriptions.** No need to construct `asset_feed_spec` JSON — plural flags do it.

CTA values: `APPLY_NOW, BOOK_TRAVEL, BUY_NOW, CONTACT_US, DOWNLOAD, GET_OFFER, GET_QUOTE, LEARN_MORE, NO_BUTTON, OPEN_LINK, SHOP_NOW, SIGN_UP, SUBSCRIBE, WATCH_MORE`.

### Step 4: Ad

```bash
AD_ID=$(meta ads ad create "$ADSET_ID" \
  --name "$AD_NAME" \
  --creative-id "$CREATIVE_ID" \
  --pixel-id "$PIXEL_ID" \
  --status PAUSED \
  --output json | jq -r '.id')
```

### Verification

```bash
meta ads campaign get "$CAMPAIGN_ID" --output json | jq .
meta ads adset get "$ADSET_ID" --output json | jq .
meta ads ad get "$AD_ID" --output json | jq .
```

---

## 7. Insights

```bash
meta ads insights get \
  --campaign-id "$CAMPAIGN_ID" \
  --date-preset last_30d \
  --time-increment daily \
  --breakdown age --breakdown gender \
  --fields spend,impressions,ctr,cpc,reach,actions,conversions,purchase_roas \
  --sort spend_descending \
  --output json
```

| Flag | Values |
|---|---|
| `--date-preset` | `today, yesterday, last_3d, last_7d, last_14d, last_30d, last_90d, this_month, last_month` |
| `--since` / `--until` | `YYYY-MM-DD` (must use both, override `--date-preset`) |
| `--time-increment` | `all_days (default), daily, weekly, monthly` |
| `--breakdown` (repeatable) | `age, gender, country, publisher_platform, device_platform, platform_position, impression_device` |
| `--sort` | `<metric>_ascending` or `<metric>_descending` |
| `--fields` | comma-separated; defaults to `spend, impressions, clicks, ctr, cpc, reach` |
| Filters | `--campaign-id`, `--adset-id`, `--ad-id` |

---

## 8. Datasets (Pixels) — net-new for the plugin

Pre-CLI, the plugin could only validate an existing pixel. Now it can create and wire one:

```bash
# Create
meta ads dataset create --name "Site Pixel" --business-id "$BUSINESS_ID"

# Connect to ad account + catalog in one call
meta ads dataset connect "$PIXEL_ID" \
  --ad-account-id "$AD_ACCOUNT_ID" \
  --catalog-id "$CATALOG_ID"

# Grant permissions
meta ads dataset assign-user "$PIXEL_ID" \
  --tasks ADVERTISE --tasks ANALYZE --tasks EDIT
```

Available tasks: `ADVERTISE, ANALYZE, EDIT, UPLOAD`. Auto-assigned on create: `ADVERTISE + ANALYZE + EDIT`.

---

## 9. Catalogs — net-new for the plugin

```bash
meta ads catalog create --name "Inventory" --vertical commerce
```

Verticals: `adoptable_pets, commerce (default), destinations, flights, generic, home_listings, hotels, local_service_businesses, offer_items, offline_commerce, transactable_items, vehicles`.

---

## 10. Exit Codes (use in routines + scripts)

| Code | Meaning | Recommended action |
|---|---|---|
| `0` | Success | Continue |
| `3` | Auth error (token expired/invalid) | Alert: "refresh `ACCESS_TOKEN`" |
| `4` | API error (Meta side) | Retry once with backoff, then alert |

In routines:

```bash
meta ads insights get --no-input --output json --date-preset yesterday > /tmp/snap.json
RC=$?
case $RC in
  0) echo "OK" ;;
  3) alert "Meta ACCESS_TOKEN expired. Run 'meta auth status' and refresh." ;;
  4) sleep 30 && meta ads insights get ... || alert "Meta API error after retry" ;;
  *) alert "Unexpected exit code $RC" ;;
esac
```

---

## 11. When the CLI Is Insufficient — fall back to raw Graph API

The CLI doesn't (yet) cover these. Use `curl` against `graph.facebook.com/v22.0/...` with the same `ACCESS_TOKEN` env var:

| Pattern | Why |
|---|---|
| Custom audiences (hashed email/phone lists) | Not in command reference |
| Lookalike audience creation | Not in command reference |
| Interest/behavior targeting (`flexible_spec`) | CLI exposes only `--targeting-countries` |
| Detailed age/gender/locale targeting | Not in flag list |
| ASC+ / Advantage+ Shopping (`existing_customer_budget_percentage`) | Not surfaced |
| Post ID relaunching (`effective_object_story_id`) | Niche pattern |
| EMQ verification (`/{pixel_id}/events?fields=event_match_quality`) | Telemetry endpoint |
| Manual `asset_feed_spec` JSON for advanced creative shapes | CLI uses simple flags only |

Fall back examples are in `api-gotchas.md` and `advantage-plus-creative.md`.

---

## 12. Common Errors

- **`meta: command not found`** — Run `uv tool install meta-ads` (preferred) or `pip install meta-ads`. The plugin's `/gtm-setup` wizard does this automatically when Meta is configured.
- **Exit code 3 on every command** — `ACCESS_TOKEN` is missing, expired, or lacks scopes. Run `meta auth status` and verify all 7 scopes listed in §2.
- **`AD_ACCOUNT_ID required`** — Add to `.env.gtm` or pass `--ad-account-id act_XXXXX`.
- **`Business admin must accept terms`** on `dataset create` — A business admin must accept the Meta Business Tools terms once. CLI prompts for this; in `--no-input` mode it fails with a clear message.

---

## 13. Versioning

Pin the CLI version in setup:

```bash
uv tool install meta-ads==<latest-stable>
```

The plugin records the installed version in `.gtm/config.json` under `meta.cli_version`. The weekly-optimization routine warns if the installed version drifts from the recorded one.
