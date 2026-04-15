# Referral Loops

## Double-Sided Referral Program

The most effective referral programs reward BOTH the referrer and the referee. Single-sided referrals (only the referrer gets rewarded) have ~60% lower participation rates because the referee feels like they're being sold to, not invited.

### Core Mechanics

```
1. Referrer generates unique link (in-app or email)
2. Referee clicks link → lands on signup page with referral code
3. Referee signs up AND completes qualifying action
4. Both receive reward simultaneously
5. Referee is prompted to become a referrer (loop continues)
```

### Qualifying Actions (Don't Reward Signups Alone)

Rewarding raw signups invites abuse. Require a qualifying action that proves real engagement:

| Product type | Qualifying action | Why |
|-------------|-------------------|-----|
| SaaS | Complete onboarding + use 1 core feature | Proves real usage intent |
| EdTech | Enroll in first course + complete 1 lesson | Proves learning intent |
| Marketplace | First transaction (buy or sell) | Proves economic intent |
| Community | Post or comment at least once | Proves participation intent |
| Free trial | Start trial + use product on 3 different days | Proves sustained engagement |

### Reward Structures

#### Credit/Discount (Best for SaaS/Subscriptions)

```
"Give $20, Get $20"
- Referrer: $20 credit toward next billing cycle
- Referee: $20 off first month
- Trigger: Referee completes qualifying action
```

**Pros:** Directly reduces churn (referrer stays for the credit), low cost per referral.
**Cons:** Only works if they're already paying or plan to.

#### Extended Trial (Best for Freemium)

```
"Invite a friend, both get 1 extra month of Pro"
- Referrer: 30 days of Pro features added
- Referee: 30 days of Pro instead of 14-day trial
- Trigger: Referee signs up
```

**Pros:** Zero cash cost, increases feature exposure, works with reverse trial model.
**Cons:** Doesn't drive revenue directly.

#### Feature Unlock (Best for Feature-Gated Products)

```
"Invite 3 friends, unlock Premium Templates forever"
- Referrer: Premium template pack unlocked permanently
- Referee: Access to 5 bonus templates
- Trigger: 3 referees complete qualifying action
```

**Pros:** Creates tiered motivation (invite more = unlock more), viral loop.
**Cons:** Requires careful feature selection (must be desirable but not core).

#### Cash/Gift Card (Best for High-Ticket)

```
"Earn $50 for every friend who subscribes"
- Referrer: $50 gift card or payout
- Referee: $50 off first purchase
- Trigger: Referee makes first payment
```

**Pros:** Universally motivating, clear value proposition.
**Cons:** Expensive, attracts referral fraud.

## Viral Coefficient Math

### K-Factor Formula

```
K = i * c

Where:
  i = average number of invitations sent per user
  c = conversion rate of those invitations (invitation → signup)
```

**Examples:**
```
Low: i=2 invitations * c=5% conversion = K=0.10
     → Each 100 users bring 10 more. Growth requires paid acquisition.

Medium: i=5 invitations * c=10% conversion = K=0.50
        → Each 100 users bring 50. Significant organic supplement.

High: i=10 invitations * c=15% conversion = K=1.50
      → Each 100 users bring 150. Viral growth (rare, usually temporary).
```

### Viral Cycle Time

K-factor alone doesn't determine speed of growth. Viral cycle time (VCT) matters:

```
VCT = time from user signup to their referrals signing up

Short VCT (1-3 days): Rapid viral growth (social apps, games)
Medium VCT (1-2 weeks): Moderate growth (productivity tools)
Long VCT (1+ month): Slow viral growth (B2B SaaS)
```

### Effective Growth Rate

```
Effective users = Acquired users / (1 - K)

At K=0.3: 100 acquired → 143 effective users (43% organic uplift)
At K=0.5: 100 acquired → 200 effective users (100% organic uplift)
At K=0.7: 100 acquired → 333 effective users (233% organic uplift)
At K=1.0: Infinite growth (theoretical; in practice, K decays over time)
```

## Increasing K-Factor

### Increase Invitations Sent (i)

**1. Make sharing frictionless:**
- Pre-filled messages: "Join me on [Product] -- here's $20 off: [link]"
- One-click sharing to WhatsApp, email, LinkedIn, Twitter
- Copy-to-clipboard referral link (always accessible, never buried)
- QR code for in-person sharing

**2. Multiply sharing touchpoints:**
- After first "aha moment" (just completed onboarding)
- After a milestone ("You just completed 10 lessons!")
- In email signatures (auto-generated referral link)
- In-app share button on content they create
- End of session prompt ("Know someone who'd love this?")

**3. Gamify referrals:**
- Referral leaderboard (top referrers get recognition)
- Tiered rewards: 1 referral → bonus A, 3 → bonus B, 10 → bonus C
- "Ambassador" status for top referrers (exclusive perks)
- Monthly contest: "Top referrer wins [prize]"

### Increase Conversion Rate (c)

**1. Social proof on the referral landing page:**
- "[Referrer name] invited you" (personal connection)
- "[X] people joined this month" (momentum)
- Testimonials from similar users

**2. Reduce friction in signup flow:**
- Pre-fill email if available from referral link
- Minimize form fields (name + email only)
- Social login (Google, Apple, GitHub)
- No credit card for trial

**3. Match incentive to motivation:**
- If referee values money: "$20 off"
- If referee values time: "Skip the waitlist"
- If referee values status: "VIP access"

## Referral Program Implementation Checklist

### MVP (Launch in 1 week)

- [ ] Unique referral link per user (generated on signup)
- [ ] Referral tracking (who referred whom)
- [ ] Qualifying action trigger
- [ ] Reward fulfillment (automatic credit/feature unlock)
- [ ] Basic referral dashboard (for the user: how many referrals, status)
- [ ] Share via email + copy link functionality
- [ ] One referral prompt (after onboarding completion)

### Growth (Add in month 2)

- [ ] WhatsApp share button (critical for LATAM)
- [ ] Social media share cards (OG image with personalized message)
- [ ] Referral leaderboard
- [ ] Tiered rewards
- [ ] Multiple touchpoint prompts
- [ ] Admin dashboard (total referrals, conversion rate, top referrers)

### Scale (Add in month 3+)

- [ ] A/B testing referral incentives
- [ ] Fraud detection (multi-account detection, referral quality scoring)
- [ ] Ambassador program (top 1% referrers get special perks)
- [ ] Referral attribution in analytics (PostHog: track referred vs organic cohorts)
- [ ] Automated lifecycle emails for referred users

## Anti-Fraud Measures

| Fraud type | Detection | Prevention |
|------------|-----------|------------|
| Self-referral | Same IP, device, or email domain | Block referrals from same device/IP |
| Fake accounts | No qualifying action completed | Require meaningful qualifying action |
| Referral farms | Burst of referrals from one user | Cap referrals at 20/month per user |
| Incentive abuse | User signs up, gets reward, cancels | Delay reward by 7 days, require retention |

## Metrics to Track

| Metric | Formula | Healthy benchmark |
|--------|---------|-------------------|
| Referral participation rate | Referrers / Total users | 10-30% |
| Invitations per referrer | Total invites / Referrers | 3-5 |
| Invite conversion rate | Signups / Invitations | 10-25% |
| Qualifying action rate | Qualified referees / Signups | 40-60% |
| K-factor | Invitations per user * Conversion rate | 0.2-0.5 |
| Referral CAC | Reward cost / Qualified referral | Should be < paid CAC |
| Referred user LTV | LTV of referred users | Typically 15-25% higher than non-referred |
