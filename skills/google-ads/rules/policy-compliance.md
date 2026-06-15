# Google Ads Policy, Compliance & Reinstatement

Enforcement doctrine and the recovery playbook (Atlas Part XIII), plus the info-product compliance minefield (Atlas Part X). Operating in competitive or sensitive niches demands a working knowledge of *what triggers a suspension*, *how to recover*, and *an honest map of the blackhat techniques so teams can recognize them, not deploy them*. This file documents the evasion anatomy for **recognition only** — it is never endorsed.

> Money note: nothing here mutates spend, but the read path still touches money in micros. CLI stats report `cost_micros` — divide by 1e6 for dollars (1,000,000 micros = $1). Diagnosis reads come from the read-only CLI (`skills/google-ads/rules/gads-cli.md`); the only writes in a reinstatement (corrected tracking templates, footer/refund updates, status flips) go through the REST `:mutate` endpoints via curl and default to status PAUSED.

## The Scale of Enforcement

Google's 2024 Ads Safety Report (released April 2025) is the anchor stat. Enforcement is now machine-speed and front-loaded — most accounts die **before a single ad serves**.

| Metric | 2024 | Prior |
| :---- | :---- | :---- |
| Advertiser accounts suspended | **39.2M** | 12.7M in 2023 (>3x growth) |
| When suspended | **Majority before any ads served** | — |
| LLM enhancements in the enforcement stack | **50+**, covering **97% of enforcement actions** | — |
| Appeal speed | **~70% faster**; **99% processed within 24h** (as of Nov 2025) | — |
| Incorrect-suspension reduction (Google's claim, Gemini) | **~80%** | — |

**Faster does not mean a higher approval rate.** A 24-hour turnaround is the *queue* getting faster, not the bar getting lower. A weak appeal now gets rejected in a day instead of a week — which means you get fewer, faster chances, not more forgiving ones. Plan every appeal as if it is your one shot (see the reinstatement framework).

## Trigger Categories

Three buckets. The first is an **egregious, no-warning** bucket — it skips straight to suspension with no strike sequence. The three-strike ladder (**warning → 3-day → 7-day → permanent**) applies **outside** the egregious buckets only.

| Bucket | What lands you here | Warning? |
| :---- | :---- | :---- |
| **Circumventing systems** | Hidden redirects, cloaking, malicious code, tracking templates that fail to match the final URL, sitelinks pointing to different content, multiple-account abuse, a cluster of disapprovals in a short window | **No — egregious, instant** |
| **Misrepresentation & unreliable claims** | Exaggerated performance claims without evidence, hidden subscription costs, missing refund/contact details, health/wealth/transformation claims | Three-strike applies |
| **Suspicious payments** | Billing details that don't match the card; multiple accounts sharing a payment method across regions | Often egregious |

The three-strike ladder, where it applies:

| Strike | Consequence |
| :---- | :---- |
| 1 | Warning |
| 2 | 3-day suspension |
| 3 | 7-day suspension |
| 4 | Permanent |

**Tracking-template / final-URL mismatch is the single most common *accidental* circumvention trigger.** An outdated dynamic tracking template that no longer resolves to the live final URL reads to the system exactly like a redirect cloak. Audit it before you ever appeal — see the reinstatement framework's root-cause step.

## Info-Product Compliance Minefield

Courses, coaching, and communities selling **money, health, or personal transformation** sit in Google's most dangerous policy territory: **Misrepresentation, Unreliable Claims, and Unacceptable Business Practices**. They are especially exposed when they:

- imply **guaranteed results**,
- imply **affiliation with a public figure**, or
- **omit critical terms and refund details**.

**Verification-first model (tightened late 2025 / January 2026):** financial-education and market-forecasting advertisers may now be required to hold **regulatory authorization before approval** — pass verification first, or the account never serves regardless of creative quality.

**What compliant operators actually ship:**

| Element | Compliant implementation |
| :---- | :---- |
| Disclaimers | Prominent, **bold** — "results vary, not guaranteed" — above the fold and in the footer, not buried |
| Proof | **Verifiable case studies with real data**, not screenshots of unverifiable income |
| Checkout | Compliant processor (**Stripe / PayPal**) with an **accessible refund policy in the footer** |
| Terms | Billing cadence, subscription renewals, and cancellation stated plainly before purchase |

They avoid the egregious no-warning buckets entirely. The honest reality: education funnels often *report* better than SaaS (WordStream by LocaliQ puts Education CVR ~13.14%) precisely because many optimize to webinar registrations or low-friction tripwires — judged-by-Google metrics flatter them. That flattery does not protect you from a Misrepresentation review.

**WHITEHAT | 10/10** — Verified case-study funnels with prominent outcome disclaimers (results vary, not guaranteed) and compliant checkout are sustainable and pass review.

**BLACKHAT | 1/10** — *Documented so you recognize it — never deploy.* Get-rich-quick / guaranteed-income / absolute-transformation claims violate the unreliable-claims policy, trigger immediate bans, and cause direct consumer harm.

**BLACKHAT | 1/10** — *Documented so you recognize it — never deploy.* Hiding offer terms, refund conditions, billing cadence, or subscription renewals is a classic suspension and consumer-harm trigger.

## The Reinstatement Framework

If suspended, **work the problem in order**. Diagnosis reads run on the read-only CLI; the remediation writes go through REST `:mutate`. Do **not** fire off an appeal before you have done the prior steps — repeated weak appeals worsen the case.

### 1. Diagnose — find the trigger

Policy Manager (in the UI) names the violation. The **change logs** show what changed right before the disapproval cluster — your most likely culprit. Pull the change history read-only (see `skills/google-ads/rules/gads-cli.md`):

```bash
# What changed, when, by whom — find the edit that preceded the suspension
google-ads-open-cli change-status <CID> --format compact

# Actor + field granularity over the window
google-ads-open-cli query <CID> "
  SELECT change_event.change_date_time, change_event.user_email,
         change_event.change_resource_type, change_event.changed_fields
  FROM change_event
  WHERE change_event.change_date_time DURING LAST_30_DAYS
  ORDER BY change_event.change_date_time DESC
  LIMIT 200
" --format compact
```

**Exit handling (read CLI):** capture stderr. If non-zero and stderr matches `/auth|token|credential|unauthenticated|permission/i` → auth error; tell the operator to re-run `google-ads-open-cli auth login`. Otherwise treat as an API error: back off and retry once. This is a different binary from Meta's — do **not** assume the literal 0/3/4 exit codes.

### 2. Remediate — fix the actual problem

Remove flagged copy, fix billing, correct redirects/tracking templates. **Fix the website and landing page first** — reinstatement specialists run **160+-step site checklists**, and the LP is where most circumvention flags actually live. The status flip and any corrected-template write go through REST and default to PAUSED:

```bash
curl -s -X POST \
  "https://googleads.googleapis.com/v18/customers/${CUSTOMER_ID}/campaigns:mutate" \
  -H "Authorization: Bearer ${GOOGLE_ADS_ACCESS_TOKEN}" \
  -H "developer-token: ${GOOGLE_ADS_DEVELOPER_TOKEN}" \
  -H "login-customer-id: ${GOOGLE_ADS_LOGIN_CUSTOMER_ID}" \
  -H "Content-Type: application/json" \
  -d '{
    "operations": [{
      "updateMask": "status,trackingUrlTemplate",
      "update": { "resourceName": "customers/'"${CUSTOMER_ID}"'/campaigns/'"${CAMPAIGN_ID}"'",
                  "trackingUrlTemplate": "{lpurl}",
                  "status": "PAUSED" }
    }]
  }'
```

### 3. Assemble the evidence pack

Suspicious-payment and identity flags die on documentation, not argument:

| Document | Must match |
| :---- | :---- |
| Articles of incorporation | The **payment-profile name, exactly** |
| Bank statements | The **card** on file |
| Server logs | Showing the **removed scripts** / corrected redirects are gone |

**Pass identity + business verification before appealing.** An appeal submitted before verification clears is wasted.

### 4. Submit ONE strong, factual appeal

Factual appeal skeleton:

1. **Root-cause analysis** + account ID. State the specific violation and the customer ID, then explain the technical cause plainly (e.g. "an outdated dynamic tracking template broke final-URL consistency") and that it was an **error, not an attempt to bypass the system**.
2. **Remediation steps.** List concrete fixes: corrected tracking templates, landing-page accessibility and mobile speed verified via URL Inspection, footer updated with the registered entity and refund policy.
3. **Documentation references.** Point to the attached evidence pack — articles of incorporation matching the payment name exactly, matching bank statements, server-log history confirming removal of outdated scripts.

**WHITEHAT | 10/10** — Completing required verification and submitting a single factual, well-documented appeal is the correct recovery path.

**GRAYHAT | 5/10** — Migrating to new domains to dodge automated flagging can trigger manual review if done excessively; allowed, but watch for policy drift — it edges toward the footprint patterns below.

## The Anatomy of Cloaking (documented, not endorsed)

*Documented so you recognize it — never deploy.* In heavily restricted verticals, some advertisers run cloaking tools that **split traffic into two destinations**: a clean **safe page** built to satisfy reviewers and crawl bots, and a **money page** (the aggressive or non-compliant offer) shown to real users. Cloaking engines fingerprint requests to decide who sees which:

| Fingerprint signal | What it discriminates |
| :---- | :---- |
| IP matching vs Google ranges | Bot/reviewer vs human |
| Browser characteristics | Headless/automation vs real client |
| Scroll behavior | Crawler vs human reading |
| Screen resolution + fonts | Datacenter vs real device |
| Geolocation | Reviewer region vs target market |

**By mid-2026 Google's detection has closed the gap.** It deploys **behavior-based flagging**, **ML crawlers that mimic human interaction** (so resolution/scroll fingerprints fail), and **cross-account footprint tracking that links and suspends connected networks**. Search Engine Land names cloaking, redirect chains, burner multi-account setups, and coded policy language directly as spammy enforcement-evasion patterns. These are suspension bait and create direct consumer harm; they belong in this atlas only so teams know what they are.

**BLACKHAT | 1/10** — *Documented so you recognize it — never deploy.* Fingerprint or redirect cloaking to bypass review carries severe risk of permanent, often **network-wide** suspension and harms consumers.

**BLACKHAT | 1/10** — *Documented so you recognize it — never deploy.* Multi-account recycling, redirect chains, coded-policy language, and burner domains are deceptive and high-risk — exactly the cross-account footprint Google's mid-2026 tracking is built to link and kill.

**GRAYHAT | 3/10** — Uploading consent-poor or policy-unclear first-party lists into Customer Match is powerful but now carries much higher risk; Search Engine Land reports misuse can trigger **immediate suspension without warning**. Allowed only with clean, documented consent — otherwise it behaves like an egregious trigger.

---

See also: `skills/google-ads/rules/gads-cli.md` (read-only diagnosis surface), `skills/google-ads/rules/conversion-tracking.md` (consent mode + the consent-faking blackhat callout), `skills/google-ads/rules/ai-max-search.md` (URL-cloaking via AI Max URL settings), and `knowledge/google-ads-atlas-2026.md` Parts X and XIII for full background.
