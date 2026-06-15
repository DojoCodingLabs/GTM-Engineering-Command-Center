# Google Ads CLI — Plugin Reference (`google-ads-open-cli`)

`google-ads-open-cli` is the plugin's primary tool for all **READ / MEASURE / AUDIT** operations on Google Ads. It wraps the Google Ads API's `GoogleAdsService.search` / GAQL surface in a clean Node binary with normalized JSON output.

**It is READ-ONLY.** It does not create, update, pause, enable, or delete anything. Every campaign write — create, update, status change, budget change, asset upload, conversion import — goes through the Google Ads REST `:mutate` API via `curl` (see `agents/campaign-operator.md`). This read/write split is the Google analog of Meta's single `meta ads` CLI, which both reads and writes through one binary. On Google, you carry **two tools**: this CLI for reads, raw REST for writes. Always be explicit in any routine or runbook which path a step takes.

Distilled from the Atlas — see `knowledge/google-ads-atlas-2026.md` (the "Atlas") Parts on auditing, GAQL, and conversion tracking for the full background. This file is the operational reference; the Atlas is the theory.

---

## 1. Install

```bash
# Global install via npm — requires Node 18+
npm install -g google-ads-open-cli
```

Contrast Meta: the `meta ads` CLI is a Python tool installed with `uv`. This one is **Node**. Different runtime, different binary, different exit-code semantics (see §6). Do not assume they behave alike.

Verify:
```bash
google-ads-open-cli --version
```

---

## 2. Auth + Configuration

Auth is **OAuth2 user credentials only**. Service accounts are **not supported** by this CLI — if your setup uses a service account for the REST write path, you still need a separate OAuth2 user flow for the read CLI.

### Interactive login (preferred for local)

```bash
google-ads-open-cli auth login \
  --developer-token=<DEVELOPER_TOKEN> \
  --client-id=<OAUTH_CLIENT_ID> \
  --client-secret=<OAUTH_CLIENT_SECRET>
```

Credentials are persisted to `~/.config/google-ads-open-cli/credentials.json` (access token + refresh token + developer token). Once logged in, subsequent commands read from that file — no flags needed.

### CI / env-var alternative (no interactive flow)

| Env var | Required | Purpose |
|---|---|---|
| `GOOGLE_ADS_ACCESS_TOKEN` | yes | Live OAuth2 access token (short-lived — refresh upstream) |
| `GOOGLE_ADS_DEVELOPER_TOKEN` | yes | From Google Ads API Center |
| `GOOGLE_ADS_LOGIN_CUSTOMER_ID` | when using an MCC | 10-digit manager account ID for manager-account access |

Env vars take priority over the stored credentials file. Use them in routines and CI where you cannot run an interactive browser login.

### Customer IDs — strip the dashes

- Customer IDs are **10 digits**. The Google Ads UI shows them as `XXX-XXX-XXXX` (e.g. `123-456-7890`). The CLI wants `1234567890` — **strip the dashes**.
- `login_customer_id` (`GOOGLE_ADS_LOGIN_CUSTOMER_ID`) is the **10-digit MCC** you authenticate *through* to reach a child account. Required whenever the target customer sits under a manager account. The `<id>` argument to most commands is the **target** customer (the account you're reading), which may differ from the login/MCC customer.

---

## 3. The Micros Convention + Output

### Money is in micros

**1,000,000 micros = $1.** This is the Google analog of Meta's "budget is in cents" gotcha — and it is worse, because the multiplier is a million, not a hundred.

- Every budget field is `amountMicros` (e.g. a $50/day budget is `50000000`).
- Every stat cost field — `cost_micros`, `average_cpc`, `average_cpm` — is in micros. **Divide by 1,000,000 for dollars.**
- `cost_micros: 12500000` → `$12.50`. Never report a micros value as dollars; always `÷ 1e6`.

Any downstream math (CPA, ROAS, n-gram waste) must convert first. A single skipped division is a 1,000,000× reporting error.

### Output format

Default output is **pretty-printed JSON**. For pipelines and `jq`, use single-line JSON:

```bash
google-ads-open-cli campaigns 1234567890 --format compact
```

`--format compact` emits one JSON object per line (NDJSON-friendly). All plugin routines use `--format compact`.

---

## 4. Command Catalog (READ-ONLY)

Every command takes the target customer id as `<id>` (10 digits, no dashes). Nothing here mutates.

### Account

| Command | Returns |
|---|---|
| `customers` | All customer accounts the authenticated user can access |
| `customer <id>` | Single account detail (currency, timezone, descriptive name) |
| `account-hierarchy <id>` | MCC → child account tree |

### Campaigns & Budgets

| Command | Returns |
|---|---|
| `campaigns <id> [--status] [--limit]` | Campaigns; filter by status, cap count |
| `campaign <id> <cid>` | Single campaign by campaign id |
| `campaign-budgets <id>` | Budgets (`amountMicros` — see §3) |

### Ad Groups & Ads

| Command | Returns |
|---|---|
| `ad-groups <id> [--campaign] [--status]` | Ad groups; filter by campaign / status |
| `ad-group <id> <agid>` | Single ad group |
| `ads <id> [--campaign] [--ad-group]` | Ads; filter by campaign / ad group |
| `ad <id> <agid> <adid>` | Single ad |

### Keywords & Negatives

| Command | Returns |
|---|---|
| `keywords <id> [--campaign] [--ad-group]` | Keywords with match types |
| `negative-keywords <id>` | Campaign/ad-group/shared-set negatives |

### Audiences / User Lists

| Command | Returns |
|---|---|
| `audiences <id>` | Audiences attached to the account |
| `user-lists <id>` | Remarketing + Customer Match lists (read state only) |

### Assets / Extensions

| Command | Returns |
|---|---|
| `assets <id> [--type]` | Assets; filter by type |
| `extensions <id>` | Sitelinks, callouts, structured snippets |

### Conversions / Billing / Change History

| Command | Returns |
|---|---|
| `conversion-actions <id>` | Conversion actions + their status/counting/category |
| `billing <id>` | Billing setup / account budgets |
| `change-status <id>` | Change history — what changed, when, by whom |

### Stats family

All take `--start YYYY-MM-DD --end YYYY-MM-DD`, optional `--segments`, and entity filters.

| Command | Grain |
|---|---|
| `campaign-stats <id> --start … --end … [--segments …] [--campaign]` | Campaign |
| `ad-group-stats <id> --start … --end … [--segments …] [--campaign] [--ad-group]` | Ad group |
| `ad-stats <id> --start … --end … [--segments …] [--campaign] [--ad-group]` | Ad |
| `keyword-stats <id> --start … --end … [--segments …] [--campaign] [--ad-group]` | Keyword |

`--segments` accepts `device,ad_network_type,day_of_week`.

**Default stats metrics** (every `*-stats` command returns these): `impressions, clicks, cost_micros, conversions, conversions_value, ctr, average_cpc, average_cpm, interactions, all_conversions`. Remember: `cost_micros`, `average_cpc`, `average_cpm` are **micros** (§3).

### Raw GAQL

| Command | Returns |
|---|---|
| `query <id> "SELECT … FROM … WHERE …"` | Arbitrary GAQL — the escape hatch when no convenience command fits |

The `query` command is the workhorse for any audit the convenience commands don't cover. Recipes in §7.

---

## 5. Plugin Defaults

| Behavior | This CLI |
|---|---|
| Output format | Pretty JSON; routines pass `--format compact` |
| Mutation | **None** — read-only by design; writes go to REST `:mutate` (§8) |
| Money unit | Micros, always — convert `÷ 1e6` before reporting (§3) |
| Customer id | 10 digits, dashes stripped (§2) |
| Auth source | Env vars override `~/.config/google-ads-open-cli/credentials.json` (§2) |

Note: the "always create as PAUSED" rule that Meta's CLI enforces at the tool level does **not** apply here — this CLI never creates anything. That rule lives on the REST write path: **all campaign writes default to status `PAUSED`** (enforced in `agents/campaign-operator.md`).

---

## 6. Normalized Exit-Handling Wrapper

This is a **different binary from `meta`** — do **NOT** assume Meta's literal `0/3/4` exit codes. The read CLI's only reliable signal is `rc != 0` plus stderr text. Classify by regex on stderr, then re-emit the plugin's normalized codes (`3` = auth, `4` = API) so downstream routines stay uniform across channels.

```bash
gads_read() {
  # Usage: gads_read <out_file> <google-ads-open-cli args...>
  local out="$1"; shift
  local err; err="$(mktemp)"
  google-ads-open-cli "$@" --format compact > "$out" 2> "$err"
  local rc=$?

  if [ $rc -ne 0 ]; then
    if grep -qiE 'auth|token|credential|unauthenticated|permission' "$err"; then
      echo "AUTH ERROR: re-run 'google-ads-open-cli auth login'" >&2
      cat "$err" >&2
      rm -f "$err"
      return 3   # normalized auth code
    else
      echo "API ERROR: backoff + retry once" >&2
      cat "$err" >&2
      rm -f "$err"
      return 4   # normalized API code
    fi
  fi
  rm -f "$err"
  return 0
}

# Caller honors the normalized codes:
gads_read /tmp/camps.json campaigns 1234567890
case $? in
  0) : ;;  # parse /tmp/camps.json
  3) alert "Google Ads auth expired — run google-ads-open-cli auth login (or refresh GOOGLE_ADS_ACCESS_TOKEN)" ;;
  4) sleep 30 && gads_read /tmp/camps.json campaigns 1234567890 || alert "Google Ads API error after one retry" ;;
esac
```

Rules:
- Capture **stderr** separately; the CLI does not give you Meta's clean integer codes.
- stderr matches `/auth|token|credential|unauthenticated|permission/i` → **auth error** → normalized exit `3` → tell the operator to re-run `google-ads-open-cli auth login` (or refresh `GOOGLE_ADS_ACCESS_TOKEN` in CI).
- Otherwise → **API error** → normalized exit `4` → backoff and retry **once**, then alert.

---

## 7. GAQL Recipes

Copy-pasteable `google-ads-open-cli query <cid>` calls. Substitute `<CID>` with the 10-digit customer id. All cost values come back in **micros** — divide downstream.

### (a) Search-term waste mining → n-grams

Pull search terms with spend and conversions over the last 30 days:

```bash
google-ads-open-cli query <CID> "
  SELECT
    search_term_view.search_term,
    metrics.cost_micros,
    metrics.conversions,
    metrics.clicks
  FROM search_term_view
  WHERE segments.date DURING LAST_30_DAYS
  ORDER BY metrics.cost_micros DESC
" --format compact > /tmp/terms.ndjson
```

Tokenize each `search_term` into 1- and 2-grams downstream and roll up cost (÷1e6) and conversions per token. High-cost / zero-conversion n-grams are negative-keyword candidates:

```bash
jq -rc '
  (.searchTermView.searchTerm) as $t
  | ($t | ascii_downcase | gsub("[^a-z0-9 ]";"") | split(" ")) as $w
  | { unigrams: $w,
      bigrams: [ range(0; ($w|length)-1) | "\($w[.]) \($w[.+1])" ],
      cost: ((.metrics.costMicros|tonumber)/1000000),
      conv: (.metrics.conversions|tonumber) }
' /tmp/terms.ndjson \
| jq -s '
  [ .[] | . as $r | ($r.unigrams + $r.bigrams)[] | {gram:., cost:$r.cost, conv:$r.conv} ]
  | group_by(.gram)
  | map({ gram: .[0].gram,
          spend: (map(.cost)|add),
          conversions: (map(.conv)|add) })
  | map(select(.conversions == 0 and .spend > 25))
  | sort_by(-.spend)
'
```

Output is ranked waste n-grams: zero conversions, spend over $25. Feed the worst into the negative-keyword `:mutate` flow (write path, §8).

> Search-term mining is the canonical safe audit. **WHITEHAT | 10/10** — you are cutting wasted spend on irrelevant queries; pure account hygiene, zero policy exposure.

### (b) Brand cannibalization %

Compare conversions on brand vs non-brand campaigns. Tag campaigns by a naming convention (e.g. brand campaigns contain `Brand`):

```bash
google-ads-open-cli query <CID> "
  SELECT
    campaign.name,
    metrics.conversions,
    metrics.cost_micros
  FROM campaign
  WHERE segments.date DURING LAST_30_DAYS
    AND campaign.status = 'ENABLED'
" --format compact \
| jq -s '
  map({ brand: (.campaign.name | test("(?i)brand")),
        conv: (.metrics.conversions|tonumber),
        cost: ((.metrics.costMicros|tonumber)/1000000) })
  | { brand_conv:    (map(select(.brand))    | map(.conv)|add // 0),
      nonbrand_conv: (map(select(.brand|not))| map(.conv)|add // 0),
      brand_cost:    (map(select(.brand))    | map(.cost)|add // 0) }
  | . + { brand_conv_pct:
            (if (.brand_conv + .nonbrand_conv) > 0
             then (.brand_conv / (.brand_conv + .nonbrand_conv) * 100)
             else 0 end) }
'
```

A high `brand_conv_pct` paired with material `brand_cost` means you are paying Google to convert demand you already own. The honest fix is to right-size brand bids and confirm incrementality.

> Bidding on your own brand to "protect" it is legitimate when a competitor is actually poaching the SERP. **GRAYHAT | 6/10** — defensible defensively, but easily becomes a way to inflate reported conversions with traffic that would have converted organically; watch the incrementality, not the raw count. (Bidding on a *competitor's* trademarked brand as a keyword is a separate, riskier tactic — see the Atlas tactic scoring; **BLACKHAT | 3/10** when it crosses into trademark-infringing ad copy.)

### (c) Zero-conversion, high-cost keyword finder

```bash
google-ads-open-cli query <CID> "
  SELECT
    campaign.name,
    ad_group.name,
    ad_group_criterion.keyword.text,
    ad_group_criterion.keyword.match_type,
    metrics.cost_micros,
    metrics.conversions,
    metrics.clicks
  FROM keyword_view
  WHERE segments.date DURING LAST_30_DAYS
    AND metrics.conversions = 0
    AND metrics.cost_micros > 50000000
  ORDER BY metrics.cost_micros DESC
" --format compact
```

`metrics.cost_micros > 50000000` = spent more than **$50** with **zero** conversions in 30 days. These are pause/negative candidates. (GAQL filters on raw micros, so the threshold is written in micros, not dollars.)

> Pausing proven-dead keywords. **WHITEHAT | 10/10** — straightforward waste elimination.

### (d) Conversion-action health

```bash
google-ads-open-cli query <CID> "
  SELECT
    conversion_action.name,
    conversion_action.status,
    conversion_action.type,
    conversion_action.category,
    conversion_action.counting_type,
    metrics.all_conversions
  FROM conversion_action
  WHERE segments.date DURING LAST_30_DAYS
" --format compact
```

Flags: `status != ENABLED` on an action you rely on; `all_conversions = 0` on an ENABLED action (tag not firing — broken tracking); a `PRIMARY` action with no recent volume. `all_conversions` includes secondary/non-bidding actions, so it is the right field for a health sweep (vs `conversions`, which is bidding-only).

> Verifying your own conversion plumbing. **WHITEHAT | 10/10** — measurement integrity, no policy surface at all.

### (e) Change-history anomaly check

Use the convenience command — it wraps `change_status` / `change_event`:

```bash
google-ads-open-cli change-status <CID> --format compact \
| jq -rc 'select(.changeStatus.lastChangeDateTime != null)
          | { when: .changeStatus.lastChangeDateTime,
              resource: .changeStatus.resourceType,
              status: .changeStatus.resourceStatus }'
```

Or raw GAQL for actor + field granularity:

```bash
google-ads-open-cli query <CID> "
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
" --format compact
```

Anomaly signals: budget or bidding-strategy changes you did not make, an unexpected `client_type` (e.g. `GOOGLE_ADS_RECOMMENDATIONS` auto-applying changes), or edits from an unknown `user_email`. This is your tamper/auto-apply audit.

> Auditing who changed what. **WHITEHAT | 10/10** — accountability and tamper detection.

---

## 8. When the CLI Is Insufficient

The single hard limit: **this CLI cannot write.** For anything that changes account state, drop to the Google Ads REST `:mutate` flow documented in `agents/campaign-operator.md`.

| Operation | Path | Notes |
|---|---|---|
| Create / update / pause / enable campaign, ad group, ad, keyword | REST `:mutate` via `curl` | All creates default to status **`PAUSED`** |
| Set / change budgets | REST `campaignBudgets:mutate` | `amountMicros` — micros (§3) |
| Add negative keywords (from §7a/§7c findings) | REST `:mutate` | The audit reads here; the fix writes there |
| **Customer Match list uploads** (hashed email/phone) | REST `offlineUserDataJobs` / Google Ads UI | **Write op — not this CLI.** This CLI's `user-lists` only *reads* list state |
| **Offline conversion / GCLID import** | REST `conversionUploads` / `offlineUserDataJobs` / UI | **Write op — not this CLI.** See `conversion-tracking.md` for payloads |
| Enhanced conversions for leads | gtag + REST upload | Write path |

Pattern: **audit with this CLI, act with REST.** A typical loop reads waste via `query` (§7), then mutates negatives/pauses via `curl` against `:mutate`. Never reach for this CLI to "just pause one thing" — it physically cannot, and the attempt wastes a turn.

---

## 9. Versioning

Pin the installed CLI version during `/gtm-setup`:

```bash
npm install -g google-ads-open-cli@<latest-stable>
```

The setup wizard records the installed version in `.gtm/config.json` under **`google_ads.cli_version`**. Routines compare the live `google-ads-open-cli --version` against the pinned value and warn on drift — a silently upgraded CLI can change field names or default metrics and break audits. Keep `google_ads.cli_version` and the actual binary in lockstep.
