# Flood & Underbid -- Contrarian Creative Testing Method

The Flood & Underbid method comes from operators spending $80M+/year on Meta Ads. It inverts conventional testing wisdom: instead of carefully testing 3-5 creatives at a time, you flood the algorithm with 100+ creatives and let the bid cap filter winners automatically.

## The Core Principle

> "Basically testing new ads for free." -- @EcomSapo

When you set a low bid cap and flood the campaign with creatives, most ads spend almost nothing because they can't compete at that bid level. Only the creatives that Andromeda predicts will convert efficiently actually spend money. Losers die naturally without burning budget.

## Structure

```
Campaign: [Product] - [Country] - Flood Test - [Date]
  Type: CBO
  Bid Strategy: Bid Cap (set at 0.7x target CPA)
  Budget: Inflated (see calibration below)
  │
  └── Ad Set: All Test Creatives
      └── 100+ visually distinct creatives
          - 10-40 ads per angle/theme
          - Each must be a unique Entity ID (different visual)
          - Text variations within same visual are fine but don't count as distinct
```

### Key Settings
- **CBO** (Campaign Budget Optimization) -- Let Meta distribute budget to winners
- **Bid Cap at 0.7x target CPA** -- If your target CPA is $30, set bid cap at $21
- **Inflated daily budget** -- Higher than you'd normally spend, because most of it won't get spent
- **ONE ad set** -- All creatives in a single ad set. Don't fragment.

## Why It Works

### The Economics

```
Scenario: 100 creatives, $30 target CPA, $21 bid cap

What happens:
  - 70-80 creatives: spend $0-5 each (losers can't compete at $21 bid)
  - 15-20 creatives: spend $10-50 each (mediocre, some delivery)
  - 5-10 creatives: absorb most of the budget (winners that Andromeda loves)

Total test cost: Much less than testing 100 creatives individually
  Traditional testing: 100 × $30 CPA × 50 conversions = $150,000
  Flood & Underbid: Most budget goes to winners, losers spend nearly nothing
```

The bid cap acts as a natural filter. Only creatives that Andromeda's Entity matching predicts will convert at or below $21 CPA get meaningful delivery. Everything else is effectively tested for free.

## The @DtcMamun Structure ($80M+ Spend)

From @DtcMamun who manages $80M+ in annual Meta spend:

> "Simple, not complex."

```
Campaign 1: CBO Testing (Bid Cap)
  └── Ad Set: Broad targeting
      └── 10-40 ads per angle
      Purpose: Find winners. Bid cap filters automatically.
      Budget: Inflated. Most won't spend.

Campaign 2: Scaling CBO (Cost Cap)
  └── Ad Set: Winners only
      └── Graduated creatives from Campaign 1
      Purpose: Scale proven winners with controlled CPA.
      Budget: Real scaling budget.
```

That's the entire structure. Two campaigns. One tests, one scales.

## When to Use

### Use Flood & Underbid When:
- You have a high volume of creative assets ready to test (20+ visuals minimum, 100+ ideal)
- You want to test many angles simultaneously without large budget commitment
- Your creative production pipeline can sustain weekly replenishment
- You have a proven target CPA from previous campaigns (needed to set the bid cap)
- Testing phase only -- not for scaling

### Do NOT Use When:
- You have fewer than 20 visually distinct creatives
- You don't know your target CPA yet (no baseline data)
- You're trying to scale (use the scaling CBO with cost cap instead)
- Your EMQ is below 7 (ARM can't rank efficiently, distorting the test)
- Brand new ad account with no pixel data (insufficient signal for Andromeda)

## Budget Calibration

### For Large Accounts ($100K-$500K/day)
Set daily budget at 2-3x what you'd normally spend on testing. The bid cap prevents overspend.

### For Smaller Accounts (Proportional Formula)

```
Daily budget = Number of creatives × Target CPA × Bid cap multiplier

Example:
  100 creatives × $30 target CPA × 0.7 bid cap = $2,100/day
  
  In practice, only 10-20 creatives will spend meaningfully.
  Actual daily spend will be $500-$1,000, not $2,100.
  The inflated budget just ensures Meta doesn't throttle winners.
```

### Important
The budget number looks scary but it's an upper bound. With a 0.7x bid cap, actual spend will be 30-50% of the stated budget because most creatives can't compete at the low bid level.

## Graduation Process

### Step 1: Run Flood Test (7 Days)

Let all 100+ creatives compete for 7 days. Don't touch anything.

### Step 2: Identify Winners

After 7 days, pull the data:
- Sort by CPA (ascending)
- Filter for creatives with 50+ conversions
- Filter for CTR above median
- These are your winners (typically 5-15% of total creatives)

### Step 3: Graduate Winners

Move winners to the dedicated scaling CBO:

```
Campaign 2: Scaling CBO (Cost Cap)
  Bid Strategy: Cost Cap (set at 1.0-1.2x target CPA)
  Budget: Real scaling budget (start at $200-500/day, scale +20% every 3-4 days)
  │
  └── Ad Set: Winners Only
      └── 5-15 graduated creatives
```

### Step 4: Refill the Flood

Replace graduated winners and dead creatives with new visuals:
- Analyze WHY winners won (which persona, messaging, hook, format)
- Produce new creatives that explore adjacent variations of winning patterns
- Reload the flood campaign with 100+ fresh creatives
- Repeat weekly

## Common Mistakes

1. **Bid cap too high** -- Setting bid cap at 1.0x target CPA defeats the purpose. The whole point is the low bid filters losers.
2. **Not enough creatives** -- 20 creatives in a flood test isn't flooding. Need 50+ minimum, 100+ ideal.
3. **Same visual, different text** -- Remember Entity Clustering. 100 text variations on 5 images = 5 entities, not 100. Need visual diversity.
4. **Touching the campaign during the 7-day test** -- Patience. Let the bid cap do the work.
5. **Using for scaling** -- Flood & Underbid is a TESTING method. Graduate winners to a separate scaling campaign.
6. **Panicking at low spend** -- If the campaign spends 30% of budget, that's working as intended. The bid cap is filtering.