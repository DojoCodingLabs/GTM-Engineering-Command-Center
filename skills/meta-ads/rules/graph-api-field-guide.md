# Graph API Field Guide — Probe-Verified Creation Surface

Field-level ground truth for creating campaigns, ad sets, creatives, and ads via the raw Graph API (v21.0+). Every rule here was verified against a live ad account by probing endpoints — not by reading documentation. Docs lag the API; the API is self-describing if you probe it correctly. Complements `api-gotchas.md` (creative-level traps) and `ads-cli.md` (CLI path) — read this when you're shaping raw API payloads or auditing existing campaigns.

---

## 1. Probe techniques (reverse-engineer any endpoint in minutes)

These work on any ad account and survive API version changes. When in doubt, probe — don't trust memory or docs.

1. **Dry-run with `validate_only`**: append `execution_options=["validate_only"]` to any create call. Full server-side validation runs; nothing is created; success returns `{"success": true}`.
2. **Enum harvesting**: send a deliberately bogus value (`"ZZZ_BOGUS"`) in one field with `validate_only`. The error message enumerates the **complete list of valid values** for that field. Zero risk, instant schema discovery.
3. **Validation is ordered** — the API reports only the FIRST failing field per call. Probe field-by-field, and satisfy earlier validations to reach later ones (e.g. include `bid_strategy=LOWEST_COST_WITHOUT_CAP`, or "Bid amount required" blocks everything behind it).
4. **Combo probing**: send plausible-but-wrong combinations to extract validity matrices from error text (e.g. a 28-day attribution window returns the exact list of supported click/view window combos for your chosen objective + optimization goal).
5. **GET-verify after every mutation**: never trust a `{"success": true}` — read the object back. **Absent fields in GET responses mean unset/empty** (Meta omits them silently; no nulls).
6. **Arrays come back normalized/sorted** (e.g. `locales [23,6]` returns `[6,23]`). Compare as sets, never order-sensitively.
7. **`metadata=1` introspection does NOT work** on Marketing API nodes (campaign/adset/ad/creative return empty metadata) — unlike core Graph nodes. Use techniques 1–6 instead.
8. **Atomic updates**: an update POST with one rejected field fails the ENTIRE call. Batch related edits deliberately; isolate risky fields.
9. **Use `curl -G --data-urlencode`** for GETs with complex `fields=` values — inline nested-field syntax in plain query strings can corrupt the request.

## 2. Immutability map (decide these at creation — there is no edit)

| Field | Editable post-create? | Notes |
|---|---|---|
| `campaign.objective` | ❌ NO | Rebuild the campaign to change |
| `adset.attribution_spec` | ❌ **NO** — error subcode **1504040**: "Attribution window update is no longer supported after adset creation. Please create a new adset instead." | The costliest trap on this page: get attribution right at create or recreate the ad set |
| `adset.is_dynamic_creative` | ❌ NO | Must be `true` at create for `asset_feed_spec` ads — else "Cannot Create Dynamic Creative ad In Non-Dynamic Creative Ad Set" |
| Ad creative (all fields) | ❌ NO | Creatives are immutable; create a new creative and swap `ad.creative` |
| `adset.optimization_goal` + `promoted_object` | ✅ YES | Editable in-place even on a live ad set — see §4 warning |
| `targeting`, `name`, `status`, budgets | ✅ YES | Targeting/optimization changes = "significant edit" → Learning Phase reset. Budget: ±20% per 3–4 days preserves learning |

## 3. API defaults ≠ UI defaults (the silent killers)

Ads Manager fills in opinionated defaults; the raw API does not. Every ad set created via API should set these **explicitly**:

| Field | API default (silent) | UI default | Set explicitly |
|---|---|---|---|
| `attribution_spec` | **7d-click ONLY** | 7d-click **+ 1d-view** | `[{"event_type":"CLICK_THROUGH","window_days":7},{"event_type":"VIEW_THROUGH","window_days":1}]` — omitting silently discards all view-through conversions from optimization + reporting |
| `degrees_of_freedom_spec` (creative) | **ALL ~80 Advantage+ creative features `OPT_OUT`** | many opted in | Decide per creative. Visual-only features (e.g. `image_brightness_and_contrast`, `enhance_cta`) are low-risk; treat text-mutating features (`text_generation`, `text_translation`, `add_text_overlay`) as high-risk for non-English or brand-sensitive copy |
| `destination_type` | `UNDEFINED` | `WEBSITE` | `destination_type=WEBSITE` for web funnels |
| `targeting.locales` | unset (all languages) | nudged per audience | Set numeric locale IDs when ads are language-specific (e.g. Spanish: `6` = es_ES, `23` = es_LA) — otherwise your ads serve to speakers of every language in the geo |
| `is_adset_budget_sharing_enabled` | must be explicit on ABO campaigns | n/a | `false` for ABO (see api-gotchas.md §12) |
| `tracking_specs` (ad) | auto-derived from `promoted_object` | same | Don't set manually; GET-verify the pixel appears |
| `conversion_domain` (ad) | unset → auto-derived | explicit | Auto-derivation works when the domain is verified in Business Manager; set explicitly otherwise |

## 4. The cross-objective optimization trap

The API **accepts** `optimization_goal` values the UI would never offer for a given objective — e.g. switching a live ad set under an `OUTCOME_TRAFFIC` campaign to `OFFSITE_CONVERSIONS` succeeds via API. The result is a configuration **Ads Manager cannot display correctly** (the conversion settings panel shows nothing), which makes human review/audit impossible. Rule: if the optimization belongs to a different objective, **rebuild the campaign under the right objective** instead of in-place switching. Conversions → `OUTCOME_SALES`.

## 5. Event-name vs enum spelling

Pixel event names and `promoted_object.custom_event_type` enums are DIFFERENT vocabularies:

| Pixel event (fbq/CAPI) | promoted_object enum |
|---|---|
| `InitiateCheckout` | `INITIATED_CHECKOUT` (past tense!) |
| `ViewContent` | `CONTENT_VIEW` (reversed!) |
| `Purchase` | `PURCHASE` |
| `AddPaymentInfo` | `ADD_PAYMENT_INFO` |

When in doubt, harvest the current enum list with technique §1.2 — a bogus probe returns all ~29 valid `custom_event_type` values.

## 6. Constraint interactions (discovered by live rejection)

- `targeting_automation.advantage_audience=1` **rejects `age_max` < 65** — age becomes a suggestion above the floor; only `age_min` is honored as a hard edge.
- Omitting `publisher_platforms` = Advantage+ placements = **Audience Network included**. If you optimize on a cheap-to-fire event (e.g. InitiateCheckout-class), AN's accidental app-taps can fire it at impossible rates, the optimizer reads "cheap conversions," and pours budget into junk — a self-reinforcing poisoning loop. Cheap-event optimization ⇒ exclude AN explicitly: `"publisher_platforms":["facebook","instagram"]`.
- `LOWEST_COST_WITH_BID_CAP` and `COST_CAP` require `bid_amount`; `LOWEST_COST_WITH_MIN_ROAS` requires `bid_constraints.roas_average_floor` AND `optimization_goal=VALUE`.
- Attribution validity depends on objective + optimization goal. For `OUTCOME_SALES` + `OFFSITE_CONVERSIONS` (v21.0): click windows {1,7} only; click×view combos exactly (1,0) (1,1) (7,0) (7,1); 28d windows are dead; `ENGAGED_VIDEO_VIEW` 1d accepted. Re-probe per your combo (§1.4).

## 7. Status model & go-live mechanics

- `status` = what you set; `effective_status` = reality. Key transient: `IN_PROCESS` (DCO ingestion/review after create or significant edit — normally resolves to ACTIVE in minutes). `WITH_ISSUES` → read `issues_info`.
- Pause cascades downward as `CAMPAIGN_PAUSED`/`ADSET_PAUSED` while children keep their own `status` — unpausing the parent restores the prior child states. This makes **campaign-level pause a safe global kill switch**.
- **Bottom-up activation** (ads → ad sets → campaign last) gives an atomic go-live moment: nothing delivers until the final campaign flip.

## 8. Diagnostics toolkit (audit any campaign from the API alone)

| Endpoint / field | What it tells you |
|---|---|
| `GET /{adset}?fields=learning_stage_info` | attribution windows, `last_sig_edit_ts` (catch accidental learning resets), learning status |
| `GET /{ad}?fields=issues_info` | delivery blockers with error levels |
| `recommendations` field (campaign/adset/ad) | Meta's own misconfiguration advice; absent = none |
| `GET /{adset}/delivery_estimate?fields=estimate_ready,estimate_dau,estimate_mau_lower_bound,estimate_mau_upper_bound` | audience-size sanity check before spending |
| `GET /{obj}/insights?breakdowns=publisher_platform` | placement-level spend/CTR — **the junk-placement detector** (AN CTRs of 20%+ on conversion campaigns = accidental-tap junk, not performance) |
| `GET /{obj}/insights?breakdowns=hourly_stats_aggregated_by_advertiser_time_zone` | intraday delivery pace — detects post-edit throttling/stalls and recovery curves |
| `GET /{campaign}/adsets?fields=...` (edge queries) | fetch all children in ONE call — strongly preferred under rate limits |

## 9. Rate-limit reality

- Hard throttle: error `code 17, subcode 2446079` ("Ad Account Has Too Many API Calls"). It reports `is_transient: false` but clears in ~2–5 minutes — treat as transient with backoff.
- Mutations + reads share the per-account budget. Prefer edge queries over per-object GET loops; batch where possible (`?batch=[...]`, 50 calls/request); monitor the `x-business-use-case-usage` response header.

## 10. Pre-flight checklist (no object goes ACTIVE without this)

1. Every create payload passed `validate_only` first.
2. GET-verify each ad set: correct `optimization_goal` + `promoted_object` (pixel + event enum), `attribution_spec` includes view-through if intended, `destination_type`, locales, placements (AN exclusion deliberate?), budget.
3. GET-verify each creative: full asset surface (≥5 bodies, ≥5 titles, descriptions, all aspect ratios), correct landing URL + tracking params.
4. Landing URLs return 200 with the pixel present.
5. Activate bottom-up; confirm `effective_status` transitions out of `IN_PROCESS`; check `issues_info` + `recommendations`.
6. First hours: placement breakdown (junk check) + hourly breakdown (pace check).
