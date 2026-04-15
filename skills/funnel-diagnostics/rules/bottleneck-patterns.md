# Bottleneck Patterns -- 15+ Diagnostic Patterns with Prescription

## Pattern Catalog

Each pattern describes a symptom, its root cause, the data to confirm it, and the prescription to fix it.

## Acquisition Bottlenecks

### Pattern A1: High CPM, Low Impressions

```
Symptom: Ads are expensive per 1,000 impressions and reach is limited.
Root cause: Audience is too narrow OR high competition for the audience.
Data to confirm:
  - Meta/Google CPM > $15 (LATAM) or > $30 (US)
  - Audience size < 100,000 (Meta Audience tool)
  - Frequency > 3 within 7 days
Prescription:
  1. Broaden targeting (remove 1-2 interest layers)
  2. Test broad targeting with smart bidding (let the algorithm find users)
  3. Expand geo-targeting (add neighboring countries)
  4. Move to different times/days if competition is time-based
Severity: High (you're paying too much to reach people)
```

### Pattern A2: High Impressions, Low CTR

```
Symptom: Ads serve but nobody clicks. CTR below 1% (Meta) or 2% (Google Search).
Root cause: Creative doesn't resonate OR targeting mismatch.
Data to confirm:
  - CTR < 1% (Meta) or < 2% (Google Search)
  - Impressions > 5,000 (sufficient data)
  - CPM is normal (rules out audience issue)
Prescription:
  1. Test 3 new creative angles (different hooks, pain points, or benefits)
  2. Check audience-creative alignment: is the message relevant to this audience?
  3. Test different ad formats (video vs static, carousel vs single)
  4. Review search terms report (Google) for relevance
  5. If video: check hook rate (3-second view rate). Below 25% = weak opening.
Severity: High (spending money showing ads nobody engages with)
```

### Pattern A3: Good CTR, High Bounce Rate

```
Symptom: People click ads but leave the landing page within 5 seconds.
Root cause: Landing page doesn't match ad promise OR page load is slow.
Data to confirm:
  - CTR > 1.5% (ad works)
  - Bounce rate > 70% (PostHog or GA)
  - Average session duration < 10 seconds
  - Page load time > 3 seconds (check Core Web Vitals)
Prescription:
  1. Check message match: does the landing page headline match the ad headline?
  2. Check page speed: LCP > 2.5s = fix immediately
  3. Check mobile experience: test at 375px width
  4. Watch 10 PostHog session recordings of bounced visitors
  5. Verify UTM parameters are correct (wrong landing page?)
Severity: Critical (paying for clicks that produce zero value)
```

## Activation Bottlenecks

### Pattern B1: Signups But No Activation

```
Symptom: Users sign up but don't complete the key activation action.
Root cause: Onboarding is confusing, too long, or doesn't deliver value fast enough.
Data to confirm:
  - Signup rate is healthy (3-10%)
  - Activation rate < 20% (for SaaS, measured as "key action within 7 days")
  - PostHog funnel shows drop-off at specific onboarding step
  - Session recordings show confusion or abandonment
Prescription:
  1. Identify the EXACT step where users drop off (PostHog funnel)
  2. Reduce time-to-value: can they see product value in < 5 minutes?
  3. Simplify onboarding: reduce steps, remove non-essential fields
  4. Add progress indicators ("Step 2 of 4")
  5. Send activation email sequence (Day 1, 2, 4, 7)
  6. Personal touch: offer live help via chat or email for first 100 users
Severity: Critical (acquiring users who never experience the product)
```

### Pattern B2: Partial Onboarding Completion

```
Symptom: Users start onboarding but abandon at a specific step.
Root cause: One step is confusing, broken, or requires too much effort.
Data to confirm:
  - PostHog funnel shows >30% drop at specific step
  - Session recordings show hesitation, rage clicks, or back-navigation at that step
  - Error logs show failures at that step (broken integration, validation error)
Prescription:
  1. Watch 20 session recordings of users who abandoned at that step
  2. Check for technical errors (console errors, API failures)
  3. Simplify the step: can it be split into 2 smaller steps?
  4. Make the step optional: move it to settings, let users skip
  5. Add contextual help (tooltip, inline instructions, video)
  6. A/B test a simpler version of the step
Severity: High (fixable, specific, high-impact)
```

### Pattern B3: Email Verification Drop-off

```
Symptom: Users sign up but never verify their email, so they can't use the product.
Root cause: Verification email is delayed, lands in spam, or users don't see the point.
Data to confirm:
  - Signup count vs verified count (>20% gap)
  - Email delivery rate for verification emails
  - Time between signup and verification (>1 hour = losing them)
Prescription:
  1. Send verification email within 30 seconds of signup
  2. Check deliverability: SPF, DKIM, DMARC properly configured?
  3. Add "Check your spam folder" messaging on the verification screen
  4. Implement magic link or one-click verify (reduces friction)
  5. Allow limited product access before verification (verify later)
  6. Resend verification email at Day 1 and Day 3
Severity: High (pure mechanical loss, no product problem)
```

## Revenue Bottlenecks

### Pattern C1: High Trial Usage, Low Conversion

```
Symptom: Trial users are active and engaged but don't upgrade to paid.
Root cause: Pricing objection, unclear value of paid tier, or bad upgrade UX.
Data to confirm:
  - Trial activation rate > 30% (users are engaged)
  - Trial-to-paid conversion < 10%
  - Usage metrics show trial users using the product regularly
  - Exit survey or cancellation reasons mention pricing
Prescription:
  1. Review pricing page: is the value of paid tier clear?
  2. Show usage-based upgrade prompts: "You've used 80% of your free limit"
  3. Offer a discount at trial end (10-20% for first 3 months)
  4. Reduce friction: one-click upgrade, save payment info early
  5. Send trial-to-paid email sequence with ROI data
  6. Consider freemium with natural upgrade triggers instead of time-limited trial
Severity: Critical (losing revenue from engaged users)
```

### Pattern C2: Cart/Checkout Abandonment

```
Symptom: Users reach the pricing/checkout page but don't complete payment.
Root cause: Pricing shock, complicated checkout, trust issues, or payment method issues.
Data to confirm:
  - Pricing page visits > checkout completions (>50% drop-off)
  - PostHog funnel shows exact checkout step where users leave
  - Stripe payment intent created but not completed
Prescription:
  1. Simplify checkout: reduce to 1-2 steps maximum
  2. Add trust signals: security badges, "Cancel anytime", money-back guarantee
  3. Offer multiple payment methods (credit card, PayPal, local methods)
  4. For LATAM: offer local currency pricing and local payment methods
  5. Exit-intent popup with a small discount or free trial extension
  6. Retargeting ads to checkout abandoners (Meta custom audience)
Severity: Critical (users want to buy but can't/won't)
```

### Pattern C3: Payment Method Failures

```
Symptom: Users attempt payment but it fails.
Root cause: Declined cards, incorrect billing info, 3D Secure failures, or unsupported payment methods.
Data to confirm:
  - Stripe dashboard: payment failure rate > 5%
  - Common decline codes: insufficient_funds, card_declined, authentication_required
  - LATAM markets: international card restrictions
Prescription:
  1. Implement Stripe Smart Retries for failed payments
  2. Add clear error messages with specific fix instructions
  3. Support local payment methods for LATAM (PIX, OXXO, Mercado Pago)
  4. Implement 3D Secure 2.0 properly (some implementations are broken)
  5. Send immediate "payment failed" email with card update link
  6. Offer annual plan at discount (fewer payment failure opportunities)
Severity: High (mechanical loss, often fixable)
```

## Retention Bottlenecks

### Pattern D1: Week 1 Drop-off

```
Symptom: Users are active in week 1 but disappear by week 2.
Root cause: Initial excitement fades, no habit loop established.
Data to confirm:
  - Week 1 retention > 60% (they liked it initially)
  - Week 2 retention < 30% (the habit didn't form)
  - No engagement between Day 7 and Day 14
Prescription:
  1. Create a "Day 8" email: remind them of progress, suggest next step
  2. Implement streak mechanics (daily login rewards, progress tracking)
  3. Send push notifications or emails for new content/activity
  4. Create a "Week 2 challenge" that deepens engagement
  5. Check if Week 1 content is significantly better than Week 2 (content quality drop)
Severity: High (losing users right after the habit window)
```

### Pattern D2: Feature-Specific Churn Correlation

```
Symptom: Users who DON'T use feature X churn at 3x the rate.
Root cause: Feature X is the core value driver; users who miss it never see the real value.
Data to confirm:
  - Cohort analysis: segment by feature X usage
  - Users WITH feature X: 80% retention at Day 30
  - Users WITHOUT feature X: 25% retention at Day 30
Prescription:
  1. Identify feature X through correlation analysis
  2. Make feature X part of the onboarding flow (required step)
  3. Highlight feature X in the activation email sequence
  4. For users who haven't used feature X by Day 3: trigger targeted prompt
  5. Consider making feature X the default view or homepage
Severity: Critical (this is your "aha moment" -- all effort should drive users here)
```

### Pattern D3: Involuntary Churn (Payment Failures)

```
Symptom: Active users are churning because their payments fail silently.
Root cause: Expired cards, insufficient funds, bank blocks on recurring charges.
Data to confirm:
  - Stripe: involuntary churn > 2% of subscriptions/month
  - Active users (logged in last 7 days) with failed payments
  - subscription.status = 'past_due' for active users
Prescription:
  1. Enable Stripe Smart Retries (retries at optimal times)
  2. Pre-dunning email 7 days before card expiry
  3. Failed payment email sequence: Day 0, Day 3, Day 5, Day 7
  4. In-app banner for users with past_due status
  5. Offer to pause instead of cancel (keeps the relationship)
  6. After 3 failed retries: personal email from founder/CS
Severity: High (these are PAYING users who WANT your product)
```

## Referral Bottlenecks

### Pattern E1: No Referral Mechanism

```
Symptom: Users love the product but have no way to share it.
Root cause: No referral program, no share feature, no incentive.
Data to confirm:
  - NPS > 40 or CSAT > 4.0 (users are happy)
  - 0% of new signups come from referral
  - No "invite" or "share" feature exists
Prescription:
  1. Add a simple share feature (copy link, email invite)
  2. Offer incentive: "Give 1 month free, get 1 month free"
  3. Ask for referrals at peak moments (after achievement, after upgrade)
  4. Make referral links trackable (unique per user)
  5. Show referral progress: "You've invited 3 friends. 2 more for your reward."
Severity: Medium (leaving growth on the table)
```

### Pattern E2: Low Referral Conversion

```
Symptom: Users share referral links but referred visitors don't sign up.
Root cause: Referral landing page doesn't convert, or incentive isn't compelling.
Data to confirm:
  - Referral links shared > 100
  - Referred visitor signup rate < 10%
  - Referral landing page bounce rate > 60%
Prescription:
  1. Create a dedicated referral landing page (not the generic homepage)
  2. Show the referrer's endorsement: "[Friend's name] thinks you'd love this"
  3. Make the incentive visible immediately (both sides of the referral)
  4. Reduce signup friction for referred users (pre-fill email, skip onboarding steps)
  5. Test different incentives (money off, extended trial, premium features)
Severity: Medium (optimization opportunity for existing mechanism)
```

## Cross-Cutting Patterns

### Pattern F1: Mobile vs Desktop Performance Gap

```
Symptom: Conversion rate on mobile is <50% of desktop.
Root cause: Landing page or app is not properly optimized for mobile.
Data to confirm:
  - Desktop CVR: 5%
  - Mobile CVR: 1.5% (>50% gap)
  - Mobile traffic is 60%+ of total
Prescription:
  1. Test at 375px, 390px, 428px (common mobile widths)
  2. Check page speed on 3G connection
  3. Verify CTA button is 48px+ touch target
  4. Check form fields: are they usable on mobile?
  5. Verify no horizontal scroll
  6. Watch 10 mobile session recordings in PostHog
Severity: Critical (majority of your traffic is mobile)
```
