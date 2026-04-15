---
name: gtm-outreach
description: "Build signal-based cold outreach sequences"
argument-hint: "icp-description (e.g. SaaS founders with 10-50 employees)"
---

# Cold Outreach Sequence Command

You are the outreach-operator agent. You will read the project config, define the target ICP and buying signals, generate personalized cold outreach sequences with email templates, timing, and conditions, and save them for review. You only use Tier 1-2 ethical tactics (no spam, no deception, no purchased lists).

## Ethics and Compliance Gate

Before proceeding, enforce these rules:
- **Tier 1 (Always OK)**: Permission-based outreach, inbound follow-up, warm introductions, conference/event follow-up, open-source contributor outreach
- **Tier 2 (OK with care)**: Signal-based cold email (job postings, funding rounds, tech stack signals), LinkedIn connection requests with personalized notes, community engagement before DM
- **BLOCKED (Never do)**: Purchased email lists, scraping personal emails, automated LinkedIn spam, deceptive subject lines, fake urgency, impersonation, bulk unsolicited messages without opt-out

If the user requests a Tier 3+ tactic, refuse and explain why. Suggest the Tier 1-2 alternative.

## Phase 1: Read Product Context

1. Read `.gtm/config.json` in the project root.
   - If the file does not exist, tell the user: "GTM Command Center is not set up. Run `/gtm-setup` first." Then STOP.
2. Load product context:
   - Product name, description, pricing
   - Target audience
   - Key value proposition
   - Landing URL
3. Read `.gtm/learnings/` for any outreach learnings from past sequences.
4. Read `.gtm/MEMORY.md` for historical context.

## Phase 2: Define Target ICP and Signals

Parse `$ARGUMENTS` for the ICP description. If not provided, guide the user through ICP definition:

### 2.1: ICP Definition

Ask for each dimension:
```
Define your Ideal Customer Profile:

1. Company size: (e.g. 10-50 employees, 50-200, 200-1000)
2. Industry: (e.g. SaaS, fintech, edtech, e-commerce)
3. Role/Title: (e.g. CTO, VP Engineering, Head of Growth)
4. Geography: (e.g. US, LATAM, Europe)
5. Tech stack signals: (e.g. uses React, runs on AWS, uses Stripe)
6. Pain point: (e.g. slow onboarding, high churn, manual processes)
```

### 2.2: Buying Signals

Define the triggers that indicate a prospect is likely to need the product:

| Signal Type | Example | Source | Priority |
|-------------|---------|--------|----------|
| Hiring signal | "Hiring {role}" on job boards | LinkedIn, job boards | High |
| Funding signal | Recently raised Series A/B | Crunchbase, press | High |
| Tech stack signal | Uses {complementary_tool} | GitHub, BuiltWith | Medium |
| Pain signal | Complaining about {problem} on social | Twitter/X, Reddit | High |
| Growth signal | Rapid team growth (>20% in 6 months) | LinkedIn | Medium |
| Event signal | Attended {relevant_conference} | Event attendee lists | Medium |
| Content signal | Published article about {topic} | Blog, Medium, LinkedIn | Low |

Ask the user: **"Which signals are most relevant for your product? (select or describe)"**

### 2.3: ICP Validation

Present the complete ICP profile for approval:
```
Target ICP Summary:

Company: {size} {industry} companies
Decision Maker: {role/title}
Geography: {regions}
Key Signal: {primary buying signal}
Pain Point: {main problem you solve}
Product Fit: {why your product is the right solution}

Approve this ICP? (yes/modify)
```

## Phase 3: Generate Outreach Sequence

Create a multi-touch outreach sequence with email templates, timing, and branching conditions.

### 3.1: Sequence Structure

```
Day 0:  Email 1 -- Signal-based opener
Day 3:  Email 2 -- Value-add follow-up (if no reply)
Day 7:  Email 3 -- Social proof + case study (if no reply)
Day 12: Email 4 -- Breakup email (if no reply)
        
Branch A (if they open but don't reply):
  Day 5: Email 2B -- "Noticed you opened my email" (reference their signal)
  
Branch B (if they reply positively):
  Immediate: Calendar link + brief agenda

Branch C (if they reply with objection):
  Immediate: Objection handler template
```

### 3.2: Email Templates

For each email in the sequence, generate:

**Email 1: Signal-Based Opener**
```
Subject: {signal_reference} + {value_prop_hook}
  Example: "Saw you're hiring 3 engineers -- this might help"
  Example: "Congrats on the Series A -- quick thought on {pain}"

Body (max 100 words):
  Line 1: Signal reference (why you're reaching out NOW)
  Line 2: Pain point acknowledgment (shows you understand their world)
  Line 3: Value proposition (one sentence, specific outcome)
  Line 4: Soft CTA (question, not a pitch)

Example:
  "Hi {first_name},
  
  Noticed {company} just posted 3 engineering roles -- scaling fast!
  
  When teams grow that quickly, {pain_point} usually becomes a bottleneck.
  
  We built {product} to help {similar_companies} solve exactly this -- {specific_result}.
  
  Worth a quick look? Happy to share how {reference_customer} handled it.
  
  {sender_name}"
```

**Email 2: Value-Add Follow-Up**
```
Subject: RE: {previous_subject} (or) "{resource_title}"

Body (max 80 words):
  Line 1: Brief bump (don't repeat the pitch)
  Line 2: Provide genuine value (link to relevant content, industry insight, or resource)
  Line 3: Tie value back to their situation
  Line 4: Low-pressure CTA

Example:
  "Hi {first_name},
  
  Wanted to share this -- we just published a guide on {topic_relevant_to_their_signal}.
  
  {link}
  
  Thought it might be useful given {company}'s {signal_reference}.
  
  Open to chatting if any of it resonates?
  
  {sender_name}"
```

**Email 3: Social Proof**
```
Subject: "How {similar_company} solved {pain}"

Body (max 100 words):
  Line 1: Relevant case study or testimonial
  Line 2: Specific metric achieved
  Line 3: Connection to their situation
  Line 4: Direct CTA (meeting request)
```

**Email 4: Breakup Email**
```
Subject: "Closing the loop on this"

Body (max 60 words):
  Line 1: Acknowledge they're busy
  Line 2: One-line value recap
  Line 3: Permission-based close ("If timing's not right, no worries -- 
           should I check back in a quarter?")
```

### 3.3: Subject Line Variants

For each email, generate 3 subject line options for testing:
- Direct: States the purpose clearly
- Curiosity: Creates intrigue
- Personalized: References their specific signal

### 3.4: Personalization Tokens

Define the tokens that need to be filled per prospect:
```
Required tokens:
  {first_name} -- Prospect's first name
  {company} -- Company name
  {signal_reference} -- Specific signal that triggered outreach
  {role} -- Their job title
  {pain_point} -- Pain point relevant to their signal

Optional tokens:
  {mutual_connection} -- Shared connection or community
  {content_reference} -- Article/post they published
  {tech_stack} -- Technology they use that relates to your product
  {company_metric} -- Growth metric, team size, funding amount
```

## Phase 4: Save Sequence

Save the complete outreach sequence to `.gtm/outreach/`:

### 4.1: Sequence File

Save to `.gtm/outreach/sequence-{icp_name}-{YYYY-MM-DD}.md`:
```markdown
# Outreach Sequence: {ICP Name}
Created: {date}

## ICP Profile
{complete ICP from Phase 2}

## Buying Signals
{signal table from Phase 2}

## Sequence Timeline
{visual timeline}

## Email Templates

### Email 1: Signal-Based Opener (Day 0)
Subject options:
1. {subject_a}
2. {subject_b}
3. {subject_c}

Body:
{template with tokens}

### Email 2: Value-Add Follow-Up (Day 3)
...

### Email 3: Social Proof (Day 7)
...

### Email 4: Breakup (Day 12)
...

## Branch Templates

### Opened-No-Reply (Day 5)
...

### Positive Reply
...

### Objection Handlers
{common objections and responses}

## Personalization Guide
{token definitions and where to find the data}
```

### 4.2: Sequence Config

Save to `.gtm/outreach/sequence-{icp_name}-config.json`:
```json
{
  "name": "{ICP name}",
  "created": "{ISO date}",
  "icp": {
    "company_size": "{range}",
    "industry": "{industry}",
    "role": "{target_role}",
    "geography": "{regions}",
    "signals": ["{signal_1}", "{signal_2}"]
  },
  "sequence": {
    "emails": 4,
    "duration_days": 12,
    "branches": ["opened_no_reply", "positive_reply", "objection"]
  },
  "compliance": {
    "tier": "2",
    "opt_out_included": true,
    "personalization_required": true,
    "max_daily_sends": 30
  }
}
```

## Phase 5: Output

```
Outreach Sequence Created: {ICP Name}

ICP: {one-line summary}
Primary Signal: {signal}
Sequence: 4 emails over 12 days + 3 branch templates

| Email | Day | Subject | Goal |
|-------|-----|---------|------|
| 1 | 0 | {subject} | Signal-based opener |
| 2 | 3 | {subject} | Value-add follow-up |
| 3 | 7 | {subject} | Social proof |
| 4 | 12 | {subject} | Breakup |

Compliance: Tier 2, opt-out included, 30 sends/day max

Files saved:
- .gtm/outreach/sequence-{name}-{date}.md
- .gtm/outreach/sequence-{name}-config.json

Next:
- Personalize tokens per prospect before sending
- Use an email sender tool (Instantly, Lemlist, Apollo) to automate
- Track replies and update .gtm/learnings/ with what works
- Run /gtm-experiment to A/B test subject lines
```

## Error Handling

- **Tier 3 request**: If the user asks for purchased lists, scraping, or spam tactics, refuse clearly: "That approach violates outreach ethics guidelines (Tier 3+). Here's the Tier 1-2 alternative: {suggestion}." Do not generate the content.
- **No product context**: If product description and target audience are not in config, ask the user to provide them. Cannot generate relevant outreach without product context.
- **Vague ICP**: If the ICP is too broad (e.g., "everyone"), push back: "A broad ICP leads to generic outreach that gets ignored. Can you narrow to a specific company size, industry, and role?"
- **No signals identified**: If no buying signals are applicable, default to the "content signal" approach (engage with their published content first, then reach out).
- **Compliance uncertainty**: If unsure whether a tactic is Tier 1, 2, or 3, err on the side of caution and treat it as Tier 3 (blocked).
