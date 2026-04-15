# Email Drip Sequences -- Architecture, Timing, and Content Patterns

## Sequence Architecture

Every drip sequence follows a decision-tree structure, not a linear list. Users branch based on behavior.

```
Welcome Sequence Entry
  │
  ├── Email 1 (Day 0, immediate): Welcome + quick start
  │   │
  │   └── Did user complete activation action within 24h?
  │       ├── YES → Branch to Engaged Path
  │       │   ├── Email 2a (Day 2): Advanced feature
  │       │   ├── Email 3a (Day 5): Social proof + community
  │       │   └── Email 4a (Day 7): Upgrade/upsell nudge
  │       │
  │       └── NO → Branch to Activation Path
  │           ├── Email 2b (Day 1): "Quick win" tutorial
  │           ├── Email 3b (Day 3): Video walkthrough
  │           ├── Email 4b (Day 5): Social proof + "others succeeded"
  │           └── Email 5b (Day 7): Direct help offer
  │
  └── Day 14: Merge back → Common retention track
```

## Timing Rules

### Optimal Send Times

| Audience | Best Days | Best Times | Worst Times |
|----------|-----------|-----------|-------------|
| B2B SaaS | Tue-Thu | 9-10am, 2-3pm local | Friday PM, weekends |
| Developer Tools | Tue-Wed | 10-11am, 7-8pm local | Monday AM, weekends |
| Consumer App | Any day | 8-9am, 7-9pm local | 2-5am |
| LATAM Market | Tue-Thu | 10-11am COT/CST, 8-9pm | Monday AM |

### Sequence Cadence Rules

```
Welcome/Onboarding sequence:
  - First email: immediate (within 60 seconds of signup)
  - Days 0-7: Can email every 1-2 days (user expects communication)
  - Days 7-14: Every 2-3 days maximum
  - After Day 14: Weekly maximum unless triggered by user action

Trial-to-paid sequence:
  - 14-day trial: Email on days 0, 3, 5, 7, 10, 12, 13, 14, 16
  - 30-day trial: Email on days 0, 3, 7, 14, 21, 25, 28, 29, 30, 33
  - Never more than 2 emails in 48 hours during trial

Win-back sequence:
  - Start 7-14 days after last activity
  - 3-5 emails over 30-45 days
  - Increasing urgency, ending with "should we close your account?"
  - If no engagement after full sequence, suppress from marketing emails
```

### Sequence Entry/Exit Rules

```
Entry conditions:
  - Only enter one sequence at a time (priority queue)
  - Priority: Trial-to-paid > Activation > Welcome > Retention > Upsell
  - If user is in trial-to-paid, do NOT also send welcome emails
  - Re-entry: Never re-enter a completed sequence (use "completed" flag)

Exit conditions:
  - User completes the goal action → Exit immediately, enter next sequence
  - User unsubscribes → Exit all sequences, move to transactional-only
  - User marks as spam → Exit immediately, flag for review
  - User doesn't engage with 3+ emails in a row → Reduce cadence or pause
```

## Email Content Patterns

### Email 1: The Welcome Email (Day 0)

This is your highest-opened email (60-80% open rate). Don't waste it.

```
Subject: "Welcome to [Product] -- here's your quick-start guide"

Structure:
  1. Warm greeting (1 sentence)
  2. Confirm what they signed up for (1 sentence)
  3. Single clear CTA: the ONE action they should take right now
  4. Brief list of what's coming (set expectations for the sequence)
  5. Personal sign-off (from a real person, not "the team")

Length: 150-250 words maximum. No essay.

What NOT to do:
  - Don't list all features (overwhelming)
  - Don't ask them to complete their profile (friction)
  - Don't include 5 different CTAs (decision paralysis)
  - Don't send a generic "thanks for signing up" with no next step
```

### Email 2-3: Value Delivery (Days 1-5)

```
Structure:
  1. Reference their signup or previous action
  2. Teach ONE thing they can do with your product
  3. Show the outcome of doing it (screenshot, result, benefit)
  4. Single CTA: "Try this now" or "See it in action"

Variations:
  - Tutorial format: Step 1, Step 2, Step 3 → Result
  - Story format: "[User name] used [feature] to achieve [result]"
  - Question format: "Did you know you can [unexpected use case]?"
```

### Email 4-5: Social Proof (Days 5-10)

```
Structure:
  1. Specific customer story (name, company, result)
  2. Quantified outcome ("saved 10 hours/week", "increased revenue 40%")
  3. Quote from the customer (real testimonial)
  4. Bridge to the reader: "You can do this too"
  5. CTA: "Start your [specific action]"

What works:
  - Specific numbers beat vague claims
  - Similar companies/roles to the reader
  - Before/after comparisons
  - "I was skeptical but..." overcoming objections
```

### Urgency Email (Trial Day -2 or -1)

```
Subject: "Your [Product] trial ends tomorrow"

Structure:
  1. Clear statement: "Your trial ends in [hours/days]"
  2. Summary of what they accomplished (pull from product data if possible)
  3. What they'll lose access to
  4. Simple pricing reminder
  5. FAQ: common objections with 1-line answers
  6. Primary CTA: "Upgrade now"
  7. Secondary CTA: "Extend trial" or "Talk to us" (lower commitment)

What NOT to do:
  - Don't be aggressive or guilt-trippy
  - Don't send more than 2 urgency emails (days -2 and -1, no more)
  - Don't use fake scarcity ("only 3 spots left" for a SaaS product)
```

## Subject Line Patterns

### Formulas That Work

```
1. Direct benefit: "Get [outcome] in [timeframe]"
   "Get your first smart contract deployed in 30 minutes"

2. Curiosity gap: "[Number] [thing] you're missing"
   "3 features you haven't tried yet"

3. Personal: "Quick question about your [product] account"
   Feels 1:1, high open rate. Use sparingly.

4. Social proof: "[Name] just [achieved result] with [Product]"
   "Maria just landed her first Web3 job with Dojo"

5. Urgency (real): "[X days] left on your trial"
   Only use for actual deadlines, never manufactured urgency.

6. How-to: "How to [do thing] (step-by-step)"
   "How to audit your first Solidity contract (step-by-step)"
```

### Subject Line Rules

```
- Length: 30-50 characters (mobile preview cuts at ~40)
- Never ALL CAPS (spam trigger)
- Never use "Free" as the first word (spam trigger)
- One emoji maximum, and only if it fits the brand (test without first)
- Include the reader's first name only in 1 out of 5 emails (overuse kills it)
- A/B test subject lines on every email with 1000+ recipients
- Preview text is as important as the subject line -- always customize it
```

## Sequence Performance Benchmarks

| Sequence Type | Open Rate | Click Rate | Conversion |
|--------------|-----------|-----------|------------|
| Welcome | 50-70% | 10-20% | N/A (goal: activation) |
| Onboarding | 40-60% | 8-15% | 20-40% activation |
| Trial-to-paid | 35-50% | 5-10% | 15-30% paid conversion |
| Retention | 25-40% | 3-8% | N/A (goal: engagement) |
| Win-back | 15-25% | 2-5% | 5-15% reactivation |
| Upsell | 30-45% | 5-10% | 3-8% upgrade |

### When to Rewrite a Sequence

```
- Open rate drops below 20% for 2+ consecutive emails → Subject line problem
- Click rate drops below 2% with normal opens → Content/CTA problem
- Unsubscribe rate above 1% on any single email → Content or cadence problem
- Sequence conversion rate below 50% of benchmark → Architecture problem (wrong emails, wrong timing)
```
