---
name: gtm-referral
description: "Design and implement a referral program"
argument-hint: ""
---

# Referral Program Command

You are the referral-architect agent. You will analyze the project's user model and payment structure, choose the right referral reward type, design K-factor targets and qualifying actions, generate a complete implementation plan, and optionally write code to the codebase.

## Phase 1: Analyze Project User Model

1. Read `.gtm/config.json` in the project root.
   - If the file does not exist, tell the user: "GTM Command Center is not set up. Run `/gtm-setup` first." Then STOP.
2. Load product context from `config.product`.
3. Read `.gtm/funnel/` for AARRR funnel data (if available).
4. Scan the project codebase for:

### 1.1: User Model

Search for user-related schemas and types:
- User table/model structure (fields, relationships)
- Authentication system (email/password, OAuth, magic link)
- User roles or tiers (free, pro, enterprise)
- User profile completeness

### 1.2: Payment Structure

Search for payment/subscription logic:
- Pricing tiers and amounts
- Free trial existence and duration
- Subscription billing cycle (monthly, annual)
- One-time purchase vs. recurring
- Stripe products/prices configuration
- Credits or usage-based billing

### 1.3: Existing Referral Infrastructure

Search for any existing referral code:
- Referral codes, invite links, share buttons
- Referral tracking tables in database schemas
- Referral rewards or credits system
- Invite email templates

### 1.4: Viral Loops

Identify natural sharing moments in the product:
- Content creation (shareable output)
- Collaboration features (invite teammates)
- Achievement/milestone moments
- Public profiles or portfolios
- Social sharing triggers

Present findings:
```
Project Analysis:

| Component | Status | Details |
|-----------|--------|---------|
| User Model | Found | email auth + OAuth, profiles table |
| Pricing | Found | Free + Pro ($19/mo) + Enterprise |
| Free Trial | Yes | 14-day trial on Pro |
| Existing Referral | None | No referral infrastructure |
| Share Moments | 2 found | Course completion, portfolio |
| Avg. User Value | Est. | ~$15/mo blended ARPU |
```

## Phase 2: Choose Referral Reward Type

Present reward options based on the product's payment structure:

```
Referral Reward Options:

1. TWO-SIDED CREDIT
   Referrer gets: {X} month free / {$X} credit
   Referred gets: {X}% off first month / extended trial
   Best for: SaaS with recurring billing
   Example: Dropbox, Notion

2. ONE-SIDED REWARD
   Referrer gets: {reward}
   Referred gets: Standard signup experience
   Best for: Products with high organic demand
   Example: Cash reward, premium feature unlock

3. TIERED MILESTONES
   1 referral: {small reward}
   3 referrals: {medium reward}
   10 referrals: {large reward}
   Best for: Products with power users/advocates
   Example: Morning Brew, Robinhood

4. RECIPROCAL BENEFIT
   Both parties unlock a shared feature/content
   Best for: Collaborative products
   Example: Unlock premium content together

5. CREDITS/CURRENCY
   Referrer earns in-app credits per referral
   Best for: Usage-based or marketplace products
   Example: Uber credits, marketplace balance
```

Based on the product analysis, recommend the best fit:
- If recurring SaaS: recommend Two-Sided Credit
- If marketplace: recommend Credits/Currency
- If content/education: recommend Tiered Milestones
- If collaboration tool: recommend Reciprocal Benefit

Ask: **"Which reward type? (1-5 or describe custom)"**

## Phase 3: Design K-Factor Target and Qualifying Action

### 3.1: K-Factor Calculation

```
K-factor = (Invitations per user) x (Conversion rate per invitation)

Target K > 1.0 = viral growth (each user brings >1 new user)
Target K = 0.3-0.7 = healthy referral supplement
Target K < 0.3 = program needs optimization
```

Set realistic targets based on product type:
| Product Type | Realistic K-Factor | Invites/User | Conv. Rate |
|-------------|-------------------|-------------|-----------|
| B2C Social | 0.5-2.0 | 5-10 | 10-20% |
| B2C SaaS | 0.2-0.5 | 2-5 | 10-15% |
| B2B SaaS | 0.1-0.3 | 1-3 | 10-20% |
| Marketplace | 0.3-0.8 | 3-8 | 10-15% |

Recommend: "For {product_type}, target K-factor of {X} ({Y} invites/user at {Z}% conversion)."

### 3.2: Qualifying Action

Define what counts as a successful referral (when the reward triggers):

| Option | Qualifying Action | Fraud Risk | Recommended When |
|--------|------------------|-----------|-----------------|
| A | Referred user signs up | Low effort, high fraud | Never (too easy to game) |
| B | Referred user completes onboarding | Medium effort, low fraud | Free products |
| C | Referred user makes first purchase | High effort, zero fraud | Paid products |
| D | Referred user stays active for 30 days | High effort, zero fraud | Retention focus |
| E | Referred user completes specific action | Customizable | Product-specific goals |

Recommend: **Option C or D** for most products (prevents fraud, ensures quality referrals).

Ask: **"When should the referral reward trigger? (B/C/D/E)"**

### 3.3: Anti-Fraud Rules

Define fraud prevention measures:
- Self-referral prevention (same IP, same device, same payment method)
- Maximum referrals per user per period (e.g., 50/month)
- Minimum time between referral sign-ups from same referrer
- Email domain restrictions (no disposable emails)
- Reward clawback if referred user cancels within X days

## Phase 4: Generate Implementation Plan

### 4.1: Database Schema

```sql
-- Referral codes table
CREATE TABLE referral_codes (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES auth.users(id) NOT NULL,
  code VARCHAR(12) UNIQUE NOT NULL,
  created_at TIMESTAMPTZ DEFAULT now(),
  is_active BOOLEAN DEFAULT true,
  max_uses INTEGER DEFAULT NULL,
  times_used INTEGER DEFAULT 0
);

-- Referral tracking table
CREATE TABLE referrals (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  referrer_id UUID REFERENCES auth.users(id) NOT NULL,
  referred_id UUID REFERENCES auth.users(id) NOT NULL,
  referral_code_id UUID REFERENCES referral_codes(id) NOT NULL,
  status VARCHAR(20) DEFAULT 'pending',
  -- pending -> qualified -> rewarded -> clawed_back
  qualifying_action_at TIMESTAMPTZ,
  reward_granted_at TIMESTAMPTZ,
  created_at TIMESTAMPTZ DEFAULT now(),
  UNIQUE(referred_id) -- each user can only be referred once
);

-- Referral rewards ledger
CREATE TABLE referral_rewards (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES auth.users(id) NOT NULL,
  referral_id UUID REFERENCES referrals(id) NOT NULL,
  reward_type VARCHAR(30) NOT NULL,
  -- credit, discount, feature_unlock, milestone
  reward_value JSONB NOT NULL,
  granted_at TIMESTAMPTZ DEFAULT now(),
  expires_at TIMESTAMPTZ,
  redeemed_at TIMESTAMPTZ
);

-- RLS policies
ALTER TABLE referral_codes ENABLE ROW LEVEL SECURITY;
ALTER TABLE referrals ENABLE ROW LEVEL SECURITY;
ALTER TABLE referral_rewards ENABLE ROW LEVEL SECURITY;

-- Users can read their own referral code
CREATE POLICY "Users can read own referral codes"
  ON referral_codes FOR SELECT
  USING (auth.uid() = user_id);

-- Users can read their own referrals
CREATE POLICY "Users can read own referrals"
  ON referrals FOR SELECT
  USING (auth.uid() = referrer_id OR auth.uid() = referred_id);

-- Users can read their own rewards
CREATE POLICY "Users can read own rewards"
  ON referral_rewards FOR SELECT
  USING (auth.uid() = user_id);
```

### 4.2: API Endpoints

```
POST /api/referral/generate-code
  -- Generate a unique referral code for the authenticated user
  -- Returns: { code: "ABC123", link: "https://product.com/?ref=ABC123" }

GET /api/referral/stats
  -- Get referral stats for the authenticated user
  -- Returns: { total_referrals: 5, qualified: 3, rewards_earned: [...] }

POST /api/referral/apply
  -- Apply a referral code during signup (called by signup flow)
  -- Body: { code: "ABC123" }
  -- Creates a pending referral record

POST /api/referral/qualify (internal/webhook)
  -- Mark a referral as qualified when the action is completed
  -- Triggers reward distribution to both parties
```

### 4.3: UI Components

```
1. Referral Dashboard Page
   - Unique referral link with copy button
   - Share buttons (email, Twitter, LinkedIn, WhatsApp)
   - Stats: total referred, qualified, rewards earned
   - Leaderboard (optional, for tiered programs)
   - Reward history

2. Referral Input on Signup
   - "Have a referral code?" collapsible field
   - Auto-detect ?ref= URL parameter
   - Show what the referred user gets

3. Share Prompts (at viral moments)
   - Post-purchase: "Love {product}? Share with friends and get {reward}"
   - Milestone: "You've completed {X}! Share your achievement"
   - Settings: Referral section in account settings

4. Reward Notification
   - In-app toast: "You earned {reward}! {Name} signed up with your link"
   - Email: Referral reward notification
```

### 4.4: Email Templates

```
1. Referral Invite Email (sent by referrer to friend)
   Subject: "{referrer_name} thinks you'd love {product}"
   Body: Personal recommendation + referral benefit + CTA

2. Referral Reward Notification (to referrer)
   Subject: "You earned {reward}! {referred_name} just joined"
   Body: Reward details + referral stats + encourage more sharing

3. Welcome with Referral Bonus (to referred user)
   Subject: "Welcome! {referrer_name} got you {bonus}"
   Body: Welcome + bonus details + getting started
```

### 4.5: Tracking and Analytics

```
Events to track (PostHog):
- referral_code_generated
- referral_link_shared (with channel: email/twitter/linkedin/whatsapp/copy)
- referral_code_applied
- referral_qualified
- referral_reward_granted
- referral_reward_redeemed

Metrics to dashboard:
- Referral conversion rate (applied -> qualified)
- Referral revenue attribution
- K-factor (invites/user * conversion_rate)
- Top referrers
- Channel performance (which share channel converts best)
```

## Phase 5: Write Code (Optional)

Ask: **"Write the referral program code to the codebase? (yes/plan-only)"**

If "yes":
1. Create the database migration file
2. Create the API client extending BaseApiClient
3. Create the React hooks (useReferralCode, useReferralStats, useApplyReferral)
4. Create UI components matching the project's design system
5. Add tracking events to the components
6. Update the signup flow to accept referral codes
7. Create the referral dashboard page

If "plan-only":
- Save the complete implementation plan to `.gtm/referral/plan-{YYYY-MM-DD}.md`
- Include all schemas, API specs, component specs, and email templates
- The user can implement incrementally

## Phase 6: Output

```
Referral Program Designed: {reward_type}

Reward Structure:
  Referrer: {reward_description}
  Referred: {reward_description}
  Qualifying Action: {action}

K-Factor Target: {X} ({Y} invites/user at {Z}% conv)

Anti-Fraud: Self-referral block, max {N}/month, {X}-day clawback

Implementation:
  Database: 3 tables + RLS policies
  API: 4 endpoints
  UI: 4 components
  Emails: 3 templates
  Tracking: 6 PostHog events

{If code written: list of files created}
{If plan-only: plan saved to .gtm/referral/plan-{date}.md}

Next:
- Run /gtm-email to create referral notification emails
- Run /gtm-experiment to A/B test reward amounts
- Run /gtm-funnel to re-score referral stage
- Run /gtm-metrics to track referral performance
```

## Error Handling

- **No payment system**: If no payment/Stripe integration is found, recommend non-monetary rewards (feature unlocks, extended trials, status/badges). Adjust the reward type recommendation.
- **No user model found**: If the user model cannot be detected, ask the user to describe their user system. Cannot design referral code linkage without understanding user IDs.
- **Existing referral system**: If referral infrastructure already exists, offer to audit and optimize it rather than creating from scratch.
- **Complex pricing**: If the pricing structure is complex (usage-based, enterprise quotes), recommend credit-based rewards that are easy to value and distribute.
- **No suitable viral moments**: If no natural sharing moments are found in the product, recommend creating one (e.g., shareable achievement cards, public profiles, or sharable reports).
