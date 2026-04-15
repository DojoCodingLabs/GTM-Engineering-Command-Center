# AARRR Pirate Metrics Framework

Reference guide for funnel health scoring, stage benchmarks, and bottleneck diagnosis.

## The Five Stages

### 1. Acquisition — How do users find you?

**Definition**: A user visits your product for the first time from any channel.

**Channels**: Paid ads (Meta, Google), organic search (SEO/GEO), referral, direct, social, email, community, outreach.

**Key Metrics**:
| Metric | Good (SaaS) | Great | Formula |
|--------|-------------|-------|---------|
| CAC (Customer Acquisition Cost) | < $50 | < $20 | Total spend / new customers |
| CPL (Cost Per Lead) | < $10 | < $5 | Ad spend / signups |
| Landing page conversion | 3-5% | 8-15% | Signups / unique visitors |
| CTR (ad click-through) | 1-2% | 3-5% | Clicks / impressions |
| Organic traffic share | 30%+ | 60%+ | Organic visits / total visits |

**Benchmark by vertical**:
- Developer tools: CAC $30-80, landing conv 5-12%
- B2B SaaS: CAC $100-300, landing conv 2-5%
- Consumer SaaS: CAC $5-30, landing conv 8-20%
- Marketplace: CAC $15-50, landing conv 3-8%

### 2. Activation — Do users experience the "aha moment"?

**Definition**: User completes the key action that demonstrates they understand the product's value.

**Examples of activation events**:
- Completed onboarding wizard
- Created first project/document/workspace
- Invited a team member
- Connected an integration
- Used core feature for the first time

**Key Metrics**:
| Metric | Good | Great | Formula |
|--------|------|-------|---------|
| Activation rate | 20-40% | 50%+ | Activated users / signups |
| Time to activation | < 1 day | < 1 hour | Median time from signup to activation event |
| Onboarding completion | 40-60% | 70%+ | Completed onboarding / started onboarding |
| Feature adoption (week 1) | 3+ features | 5+ features | Unique features used in first 7 days |

**Benchmark by vertical**:
- Developer tools: activation 30-50% (code-heavy = higher friction)
- B2B SaaS: activation 20-35% (complex setup)
- Consumer SaaS: activation 40-60% (simpler onboarding)
- Freemium: activation 15-30% (many casual signups)

### 3. Retention — Do users come back?

**Definition**: Users return to the product after their initial session and continue using it.

**Key Metrics**:
| Metric | Good | Great | Formula |
|--------|------|-------|---------|
| D1 retention | 30-40% | 50%+ | Users active day after signup / signups |
| D7 retention | 15-25% | 30%+ | Users active 7 days later / signups |
| D30 retention | 8-15% | 20%+ | Users active 30 days later / signups |
| Weekly active users (WAU) | Growing | >10% MoM | Unique users per week |
| Monthly churn rate | < 5% | < 2% | Churned users / start-of-month users |
| Net revenue retention (NRR) | 100-110% | 120%+ | (MRR + expansion - contraction - churn) / starting MRR |

**Benchmark by vertical**:
- Developer tools: D7 20-35%, monthly churn 3-5%
- B2B SaaS: D7 25-40%, monthly churn 2-5%
- Consumer SaaS: D7 15-25%, monthly churn 5-10%

### 4. Revenue — Do users pay?

**Definition**: Users convert from free to paid, or expand their spending.

**Key Metrics**:
| Metric | Good | Great | Formula |
|--------|------|-------|---------|
| Free-to-paid conversion | 3-5% | 8-15% | Paid users / free signups |
| Trial-to-paid conversion | 15-25% | 30%+ | Paid / trial users |
| ARPU (avg revenue per user) | Varies | Growing MoM | Total revenue / total users |
| MRR growth rate | 10-15% MoM | 20%+ MoM | (MRR end - MRR start) / MRR start |
| LTV (lifetime value) | > 3x CAC | > 5x CAC | ARPU × (1 / monthly churn rate) |
| LTV:CAC ratio | 3:1 | 5:1+ | LTV / CAC |
| Payback period | < 12 months | < 6 months | CAC / monthly ARPU |
| Expansion revenue | 10-20% of MRR | 30%+ | Upsells + cross-sells / total MRR |

**Benchmark by vertical**:
- Developer tools: free-to-paid 2-5%, LTV:CAC 3-5:1
- B2B SaaS: trial-to-paid 15-25%, LTV:CAC 3-7:1
- Consumer SaaS: free-to-paid 2-4%, LTV:CAC 2-4:1

### 5. Referral — Do users bring others?

**Definition**: Existing users actively drive new user acquisition.

**Key Metrics**:
| Metric | Good | Great | Formula |
|--------|------|-------|---------|
| K-factor (viral coefficient) | 0.1-0.3 | 0.5+ | Invites per user × conversion rate |
| Referral rate | 5-10% | 20%+ | Users who referred / total users |
| NPS (Net Promoter Score) | 30-50 | 60+ | % promoters - % detractors |
| Referral CAC | < 50% of paid CAC | < 25% | Referral program cost / referred customers |
| Organic/word-of-mouth share | 20-30% | 50%+ | Organic signups / total signups |

**Benchmark by vertical**:
- Developer tools: K-factor 0.1-0.3, NPS 40-60
- B2B SaaS: K-factor 0.05-0.2, NPS 30-50
- Consumer SaaS: K-factor 0.2-0.5, NPS 30-50
- Marketplace: K-factor 0.3-0.8, NPS varies

## Funnel Health Scoring Algorithm

Each stage gets a health score (0-100):

```
score = (benchmark_score × 0.4) + (trend_score × 0.3) + (relative_score × 0.3)

benchmark_score: Performance vs industry benchmarks
  - At or above benchmark: 80-100
  - Within 80% of benchmark: 60-80
  - Below 50% of benchmark: 0-60

trend_score: Week-over-week direction
  - Improving > 10%: 90-100
  - Stable (within 5%): 60-80
  - Declining > 10%: 0-40

relative_score: Drop-off compared to other stages
  - Smallest drop-off in funnel: 90-100
  - Average drop-off: 50-70
  - Largest drop-off in funnel: 0-40
```

## Bottleneck Priority Rule

When multiple stages score low, fix the one **closest to revenue** first:
1. Revenue (pricing, checkout, payment) — fix first
2. Retention (engagement, stickiness) — fix second
3. Activation (onboarding, first value) — fix third
4. Acquisition (traffic, ads, SEO) — fix fourth
5. Referral (viral loops, sharing) — fix last

Rationale: Fixing bottom-of-funnel multiplies the value of everything above it. Fixing top-of-funnel without fixing bottom just sends more users into a leaky bucket.

## Cross-Stage Correlation Patterns

| Pattern | Diagnosis | Action |
|---------|-----------|--------|
| High traffic + low signups | Landing page problem | /gtm-landing |
| Good signups + low activation | Onboarding friction | /gtm-email (activation drip) |
| Good activation + low retention | No engagement loop | /gtm-email (retention drip) |
| Good retention + low revenue | Pricing or monetization gap | /gtm-experiment (pricing test) |
| Good revenue + zero referrals | Missing viral mechanics | /gtm-referral |
| High CPA + good post-click conversion | Ad targeting too broad | /gtm-plan (tighter audiences) |
| Low CPA + poor post-click conversion | Landing-ad mismatch | /gtm-landing (match ad angle) |
| Good email open rate + low click rate | Email copy problem | /gtm-email (copy variants) |
| Good email click rate + low conversion | Landing page problem | /gtm-landing |
| Declining organic traffic | SEO regression or algorithm change | /gtm-seo (audit) |
