# Reverse Trial Mechanics

## What Is a Reverse Trial?

A reverse trial flips the traditional free trial model. Instead of giving limited access and hoping users upgrade, you give FULL premium access for a fixed period, then downgrade them to the free tier.

**Traditional trial:** Free tier → (hope) → Paid tier
**Reverse trial:** Full paid tier → (loss aversion) → Free tier → (urgency) → Paid tier

This works because loss aversion is 2x more motivating than potential gain (Kahneman & Tversky, Prospect Theory). People hate losing something they already have more than they desire something they don't yet have.

## Implementation Architecture

### Day 0: Signup

User creates an account and immediately receives full VIP/Premium access:
- No credit card required (reduces signup friction)
- Full feature access from minute one
- Welcome email emphasizes what they have access to (anchor the value)

```
Welcome email subject: "Your VIP access is active -- here's everything you can do"

Body:
"Welcome to [Product]! You have full VIP access for the next 14 days.

Here's what's included:
- [Premium Feature 1] -- most users save 5 hours/week with this
- [Premium Feature 2] -- unlock insights competitors don't have
- [Premium Feature 3] -- collaborate with unlimited team members

Start exploring now -- your VIP experience begins today."
```

### Days 1-11: Value Delivery

During the trial, focus on driving feature adoption (not selling):

- **In-app tooltips** highlighting premium features as they discover them
- **Usage tracking** -- record every premium feature they use (for the downgrade email)
- **Milestone celebrations** -- "You just saved your 10th hour this week!"
- **No sales emails during this period** -- let the product sell itself

Key metrics to track per user:
```
- premium_features_used (count of unique premium features accessed)
- sessions_count (total login sessions)
- content_created (projects, files, items they'd lose access to)
- collaboration_events (team members invited, shared items)
- time_saved_estimate (calculated from feature usage)
```

### Day 12: Warning Email

```
Subject: "Your VIP access ends in 2 days"

"[Name], your VIP access expires on [date].

Here's what you've accomplished with VIP in the last 12 days:
- Used [Feature X] 23 times
- Created [N] projects
- Saved approximately [X] hours

After [date], these features will be locked:
- [Feature 1] -- you used this 15 times
- [Feature 2] -- you used this 8 times
- [Feature 3] -- your team relied on this daily

Upgrade now to keep everything: [CTA Button]

Or keep your free account -- your data is safe either way."
```

### Day 13: In-App Banner

Show a persistent (but dismissable) banner:
```
"VIP access ends tomorrow. You've used 7 premium features this week. 
[Upgrade to keep access] or [Continue with free plan]"
```

### Day 14: Downgrade

The downgrade MUST be:
1. **Noticeable** -- User immediately sees what changed (locked features, limited access)
2. **Not destructive** -- Never delete their data, projects, or content
3. **Reversible** -- One click to upgrade and restore everything

```
Downgrade email subject: "Your VIP access has ended"

"[Name], your VIP access is now over. Here's what changed:

LOCKED:
- [Feature 1] -- you used this 23 times (locked)
- [Feature 2] -- your 5 team members can no longer collaborate (locked)
- [Feature 3] -- advanced analytics are hidden (locked)

STILL AVAILABLE:
- Your data is safe and accessible
- [Basic Feature 1] still works
- [Basic Feature 2] still works

Upgrade to VIP: [CTA Button -- prominently placed]

Monthly: $X/month | Annual: $X/month (save X%)
"
```

### Day 16: The "Miss Me?" Email

```
Subject: "You've been on free for 2 days -- here's what you're missing"

"Since your VIP ended, here's what's happened:

- [Feature] would have saved you ~2 hours today
- Your team can no longer access [shared resource]
- You missed [X] insights from the advanced dashboard

87% of users who tried VIP chose to upgrade. Ready to join them?

[Upgrade Now] -- takes 30 seconds"
```

### Day 21: Social Proof Email

```
Subject: "What other [role/industry] professionals chose"

"[Name], we checked in with others in [industry] who tried VIP:

- 87% upgraded within 30 days
- Average [metric] improvement: 34%
- Most-used premium feature: [Feature Name]

Your free account is great for getting started, but VIP is 
where the real results happen.

[See VIP plans]"
```

### Day 30: Last Chance Offer

```
Subject: "One-time offer: reactivate VIP at 40% off"

"[Name], it's been 30 days since your VIP ended.

We want you back. For the next 24 hours only, reactivate VIP 
at 40% off your first 3 months:

Monthly: $X/month → $X/month (save $X)

This offer expires at midnight [timezone] on [date].
After that, it's back to regular pricing.

[Reactivate VIP at 40% Off]"
```

## Messaging Psychology

### Loss Aversion Levers

| Lever | How to use it | Example |
|-------|--------------|---------|
| Quantified loss | Show exactly what they lose | "You used this feature 23 times" |
| Sunk cost | Remind them of work already done | "Your 12 projects are still there" |
| Social proof | Show what peers chose | "87% of users upgraded" |
| Deadline | Create time pressure on the offer | "This price expires in 24 hours" |
| Contrast | Show free vs VIP side by side | Comparison table in downgrade email |

### What NOT to Do

- **Never delete data** -- Destroying user work to force upgrades creates resentment, not sales
- **Never nag constantly** -- Max 1 email per upgrade touchpoint (days 12, 14, 16, 21, 30)
- **Never block critical workflows** -- If they created content, they must still access it (read-only is fine)
- **Never fake urgency** -- "This offer expires" must be real. Resetting the timer destroys trust
- **Never spam after day 30** -- If they haven't upgraded, switch to quarterly check-ins

## Key Metrics to Track

| Metric | Target | Red flag |
|--------|--------|----------|
| Trial to paid conversion rate | 15-25% | Below 10% |
| Time to first premium feature use | Within 24 hours | After 72 hours |
| Premium features used during trial | 3+ | Fewer than 2 |
| Downgrade to upgrade (within 30 days) | 5-10% of downgraded users | Below 3% |
| Day-30 offer redemption rate | 10-15% | Below 5% |

## Comparison: Reverse Trial vs Traditional Trial

| Dimension | Traditional Trial | Reverse Trial |
|-----------|-------------------|---------------|
| Signup conversion | Higher (free tier is simple) | Higher (full access is enticing) |
| Feature discovery | Low (limited features available) | High (everything available) |
| Upgrade motivation | Gain (want new features) | Loss (don't want to lose features) |
| Conversion rate | 5-10% | 15-25% |
| Data to personalize | Limited | Rich (full usage history) |
| Risk of gaming | Low | Medium (users may re-signup) |

### Anti-Gaming Measures

- Limit to 1 reverse trial per email address
- Require email verification before trial activation
- Track device fingerprint to prevent multi-account abuse
- Make the free tier genuinely useful (so they stay even if they don't upgrade)
