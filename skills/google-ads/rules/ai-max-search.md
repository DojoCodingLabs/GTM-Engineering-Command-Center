# AI Max for Search — Cautious Optimism, Not Blind Adoption

Distilled from **Atlas Part VII**. AI Max is the most important new Search control surface in 2026. The correct posture is cautious optimism: an 84% neutral-or-negative base rate (see evidence below) means **default skepticism** and contained, account-level experiments — never an account-wide flip on a partner's say-so.

Execution is HYBRID. Inspecting whether AI Max is on, pulling its stats, and auditing query expansion is READ-ONLY via the `google-ads-open-cli` (see `skills/google-ads/rules/gads-cli.md`). Turning AI Max on/off and setting brand/text/URL controls is a WRITE via the Google Ads REST `:mutate` endpoints over curl — no first-party CLI mutates.

## What It Is

AI Max is a **one-click feature SUITE layered onto an existing Search campaign — NOT a standalone campaign type.** There is no "AI Max campaign" to create; you toggle it on a campaign you already run. Toggling it on enables three things at once:

- **Search-term matching** — broad / keywordless expansion. Google serves your ad on queries you never added as keywords, the way broad match + smart bidding discovers terms, but without the keyword anchor. **This piece cannot be turned off** while AI Max is on; accepting AI Max means accepting keywordless expansion.

- **Text customization** — Gemini generates headlines and descriptions on the fly, assembled to the live query + the landing page. You provide raw RSA assets; Gemini rewrites and recombines them per impression.

- **Final URL expansion** — sends the user to the most relevant subpage Google can find, overriding the Final URL you set on the ad.

It is also the **migration destination for Dynamic Search Ads** — DSA migration into AI Max was **extended to February 2027** (you have runway, but the clock is real). Separately, **Automatically Created Assets** and **campaign-level broad match begin auto-upgrading in September 2026** — so even accounts that never deliberately opt in get pulled toward this surface. Audit every Search campaign before those two dates and decide opt-in vs. opt-out per campaign rather than discovering the change in a stats drop.

## The Control Levers

Four levers constrain the automation. Use all of them — an AI Max campaign without guardrails is the gray-hat failure mode below.

- **Brand settings.** Inclusions define which brands you SHOULD appear alongside; exclusions prevent serving next to specific competitors or sensitive topics. Mirror your branded-Search and PMax brand-exclusion lists here so AI Max does not cannibalize cheaper branded traffic the way PMax does by default.

- **Text guidelines.** Define messaging rules, exclude promotional terms, and **block up to 25 words globally** to constrain the generative copy engine. **Critical for compliance-sensitive categories** (finance, health, legal, crypto). Block claim words — "guaranteed," "risk-free," "#1," "best" — before Gemini can generate them into a headline you never approved. The 25-word global block is your hard ceiling on generative drift; spend it deliberately.

- **URL inclusions / exclusions.** Restrict Final URL expansion to verified landing pages so paid traffic never lands on a privacy policy, a utility page, or an internal blog post. If you cannot enumerate the pages you want, you are not ready to enable URL expansion.

- **Location-of-interest targeting.** Targets users by location of interest, not just physical or intent location. Validate it does not widen geo beyond your serviceable area before you trust the conversion numbers.

**Sam Clarke (Crossmedia) field note:** disabling dynamic ad copy AND landing-page selection while **keeping query expansion** produced good results. Query expansion is the one piece you cannot disable — so if you adopt AI Max, you are accepting keywordless expansion no matter what. Decide if that is acceptable before you toggle.

### Read the current state (READ-ONLY, gads-cli)

AI Max settings surface on the campaign. Inspect with raw GAQL via the CLI (see `gads-cli.md`):

```bash
# Is AI Max / keywordless expansion in play? Check campaign + recent search terms.
google-ads-open-cli campaign <campaign_id> <customer_id> --format compact
google-ads-open-cli query <customer_id> \
  "SELECT search_term_view.search_term, metrics.clicks, metrics.cost_micros, metrics.conversions
   FROM search_term_view
   WHERE segments.date DURING LAST_30_DAYS
   ORDER BY metrics.cost_micros DESC"
```

`cost_micros` is in **MICROS: divide by 1,000,000 for dollars** (1,000,000 micros = $1). This is the Google analog of Meta's "cents" gotcha — every money field on every stats call is micros. A "20000000" budget is **$20**, not $20M.

### Write the toggle/controls (WRITE, REST :mutate)

No first-party CLI mutates AI Max. Use the REST `campaigns:mutate` / `campaignCriteria:mutate` endpoints over curl. **All campaign writes default to status PAUSED** — bring an AI Max experiment up paused, verify brand/text/URL guardrails are attached, then enable.

```bash
curl -s -X POST \
  "https://googleads.googleapis.com/v18/customers/${CUSTOMER_ID}/campaigns:mutate" \
  -H "Authorization: Bearer ${GOOGLE_ADS_ACCESS_TOKEN}" \
  -H "developer-token: ${GOOGLE_ADS_DEVELOPER_TOKEN}" \
  -H "login-customer-id: ${GOOGLE_ADS_LOGIN_CUSTOMER_ID}" \
  -H "Content-Type: application/json" \
  -d '{
    "operations": [{
      "updateMask": "status,searchAdsSetting.optInSearchTermMatching",
      "update": { "resourceName": "customers/'"${CUSTOMER_ID}"'/campaigns/'"${CAMPAIGN_ID}"'",
                  "status": "PAUSED" }
    }]
  }'
```

**Exit handling (read CLI):** capture stderr. If non-zero and stderr matches `/auth|token|credential|unauthenticated|permission/i` → auth error; tell the operator to re-run `google-ads-open-cli auth login`. Otherwise treat as an API error: back off and retry once. Do NOT assume Meta's literal 0/3/4 exit codes — this is a different binary.

## Google's Claims vs Independent Evidence

Google markets AI Max as ~**7% more conversions** (non-retail tests) / **14%** / **27% more conversions** at similar CPA or ROAS depending on the framing. **Treat all three as marketing.** The independent picture is more sobering and more useful:

| Source / test | Finding | Type |
|---|---|---|
| **Brainlabs** — 23 tests, 16 mature accounts (Andy Goodwin via SEL) | Success rate **40% higher** with all three features on; weighted Quality Score **6.8 → 7.3**; but only **46% of new queries were truly new** | Independent testing |
| **Adriaan Dekker** — LinkedIn poll of PPC pros | **16% good** performance / **84% neutral-or-negative** | Independent poll |
| **Smarter Ecommerce** — 250+ campaigns (via PPC.Land) | Median revenue **+13%** but CPA **+16%**; only **22% near target**; AI Max active in just **12%** of 600+ accounts | Independent analysis |
| **PPC Live** — lead-gen test | Clicks **~3x**, CPC **−59%**, but conversions **−38%** and cost per lead nearly **doubled to $850** | Independent test |
| **ClickUp** (Google case study) | +20% incremental conversions, +16% ROAS, −22% CPA, +15% CVR | **Google marketing — discount** |
| **Lufthansa Group** (Google case study) | Consolidated campaigns 66%; +24% ROAS | **Google marketing — discount** |

The pattern: more reach, cheaper clicks, **worse downstream conversion economics** in lead-gen unless guardrailed. Ecommerce with clean signals fares better than lead-gen. The case studies are sales collateral; weight the independent rows.

## The Synthesis

- **Full-stack beats partial.** AI Max works best as a **full-stack toggle (all three features on)** in accounts that already have **clean conversion signals, sufficient volume, and message guardrails**. **Partial adoption is the worst outcome** — half-automated, half-controlled, and you can't attribute either.
- **Regulated/claims-heavy advertisers** can **legitimately keep text customization or URL optimization off**. That is a defensible compliance choice, not a failure to adopt — query expansion still runs underneath.
- **Default to skepticism.** The 84% neutral-or-negative base rate means: run AI Max as a **contained experiment, measured at the ACCOUNT level for true incrementality** — not at the campaign level where keywordless expansion borrows credit from your branded and exact-match traffic.
- **Kill criteria.** If **account-level CPL / CAC worsens after 2–4 weeks**, turn it off. Don't wait for "the algorithm to learn" past one month — the independent lead-gen data shows the worsening is often structural, not a learning-period artifact.

### Ethical callouts (Atlas scores preserved)

**WHITEHAT | 8/10** — AI Max with strict URL + brand exclusions plus text-guideline compliance filtering is a compliant, opt-in layer; the only risk is to performance and control, so guardrail it and measure incrementally.

**GRAYHAT | 4/10** — Blindly migrating DSA or broad-only campaigns into AI Max **without message guardrails** can expand into off-brand or compliance-risk territory; allowed, but watch for policy drift on every search-term pull.

**BLACKHAT | 2/10** — Documented so you recognize it — never deploy. Using AI Max URL settings to show crawlers compliant landing pages while sending searchers somewhere else is dynamic-sitelink / URL cloaking; it is policy-violating and a path to account suspension.
