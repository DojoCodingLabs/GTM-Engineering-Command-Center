# Email Deliverability -- DNS, Warmup, and Inbox Placement

## The Deliverability Stack

```
Deliverability depends on (in order of impact):
  1. Domain authentication (SPF, DKIM, DMARC)    — 40% of inbox placement
  2. Sending reputation (IP + domain)             — 30% of inbox placement
  3. Content quality (spam triggers, engagement)   — 20% of inbox placement
  4. List hygiene (bounces, complaints, inactive)  — 10% of inbox placement
```

## DNS Authentication Setup

### SPF (Sender Policy Framework)

SPF tells receiving servers which IPs are authorized to send email for your domain.

```dns
; TXT record on your domain
v=spf1 include:_spf.google.com include:amazonses.com include:sendgrid.net ~all

; Breakdown:
; v=spf1              — Version identifier
; include:_spf.google.com — Google Workspace can send
; include:amazonses.com   — Amazon SES can send (Resend uses SES)
; include:sendgrid.net    — SendGrid can send
; ~all                — Soft fail for all other senders (recommended over -all)
```

Rules:
- Maximum 10 DNS lookups (includes nested `include:` records)
- Each `include:` counts as 1 lookup, plus its own nested lookups
- Exceeding 10 lookups = SPF permerror = treated as no SPF
- Use `~all` (soft fail) not `-all` (hard fail) to avoid false rejections
- Check with: `dig TXT yourdomain.com` or `nslookup -type=TXT yourdomain.com`

### DKIM (DomainKeys Identified Mail)

DKIM cryptographically signs your emails so recipients can verify they weren't altered in transit.

```dns
; CNAME records (provider-specific, example for Resend)
resend._domainkey.yourdomain.com  CNAME  resend._domainkey.resend.com
resend2._domainkey.yourdomain.com CNAME  resend2._domainkey.resend.com

; For SendGrid
s1._domainkey.yourdomain.com  CNAME  s1.domainkey.uXXXXXX.wlXXX.sendgrid.net
s2._domainkey.yourdomain.com  CNAME  s2.domainkey.uXXXXXX.wlXXX.sendgrid.net
```

Rules:
- DKIM key length: 2048-bit minimum (1024-bit is deprecated)
- Each email provider needs its own DKIM selector
- Rotate DKIM keys annually (most providers handle this automatically)
- Verify with: check email headers for `dkim=pass`

### DMARC (Domain-based Message Authentication, Reporting & Conformance)

DMARC tells receiving servers what to do when SPF or DKIM fails.

```dns
; TXT record at _dmarc.yourdomain.com
v=DMARC1; p=quarantine; rua=mailto:dmarc@yourdomain.com; pct=100; adkim=r; aspf=r

; Policy progression (start lenient, tighten over time):
; Month 1:  p=none      (monitor only, no enforcement)
; Month 2:  p=quarantine; pct=25  (quarantine 25% of failures)
; Month 3:  p=quarantine; pct=100 (quarantine all failures)
; Month 6+: p=reject     (reject all failures -- only after confirming no legit senders are failing)
```

Fields:
- `p=none|quarantine|reject` — Policy for failures
- `rua=mailto:` — Where to send aggregate reports
- `ruf=mailto:` — Where to send forensic reports (optional)
- `pct=` — Percentage of messages to apply policy to
- `adkim=r|s` — DKIM alignment (r=relaxed, s=strict)
- `aspf=r|s` — SPF alignment (r=relaxed, s=strict)

## IP & Domain Warmup

### Why Warmup Matters

New IP addresses and domains have no reputation. ISPs (Gmail, Outlook, Yahoo) treat unknown senders with suspicion. Sending 10,000 emails on day 1 from a new domain = most go to spam.

### Warmup Schedule (New Dedicated IP)

| Day | Emails/Day | Notes |
|-----|-----------|-------|
| 1-2 | 50 | Send to your most engaged contacts only |
| 3-4 | 100 | Continue with engaged contacts |
| 5-6 | 250 | Expand to recently active contacts |
| 7-8 | 500 | Mix of engaged and moderately active |
| 9-10 | 1,000 | Include broader segment |
| 11-14 | 2,500 | General active contacts |
| 15-21 | 5,000 | Full active list segments |
| 22-28 | 10,000 | Approach full volume |
| 29+ | Full volume | Monitor and maintain |

### Warmup Rules

```
1. Start with your BEST contacts (highest engagement, most recent)
2. Never send to bounced, unsubscribed, or complaint addresses during warmup
3. Monitor bounce rate daily — if >5%, slow down
4. Monitor spam complaint rate — if >0.3%, stop and diagnose
5. Send consistently (same time, same volume) — spikes trigger filters
6. Include clear unsubscribe links from day 1
7. Use a mix of plain text and HTML (plain text emails have higher inbox placement)
8. Warmup period: minimum 2-4 weeks for shared IPs, 4-8 weeks for dedicated IPs
```

### Shared IP vs Dedicated IP

| Feature | Shared IP | Dedicated IP |
|---------|-----------|-------------|
| Reputation | Shared with other senders | Yours alone |
| Warmup needed | No (already warm) | Yes (4-8 weeks) |
| Volume requirement | Any | 25,000+/month to maintain reputation |
| Control | Low | Full |
| Risk | Others' bad behavior affects you | Only your behavior matters |
| Best for | Low-volume senders (<25K/month) | High-volume (>50K/month) |

Recommendation: Start with shared IP (default for Resend, SendGrid). Move to dedicated IP only when sending 50K+/month consistently.

## Spam Triggers to Avoid

### Subject Line Triggers

```
HIGH RISK (avoid always):
  - ALL CAPS in subject: "FREE MONEY NOW"
  - Excessive punctuation: "Don't miss this!!!"
  - Spam words as first word: "Free", "Congratulations", "Winner"
  - Dollar signs: "$$$", "Save $$$"
  - "Act now", "Limited time", "Once in a lifetime"

MODERATE RISK (use carefully):
  - "Re:" or "Fwd:" when it's not a reply/forward (deceptive)
  - Emoji overuse (1 is fine, 3+ triggers filters)
  - "Urgent" (test with your audience -- sometimes works in B2B)
```

### Content Triggers

```
HIGH RISK:
  - Image-only emails (no text) — filters can't read them, assume spam
  - Too many links (>5 in a short email)
  - URL shorteners (bit.ly, tinyurl) — associated with phishing
  - Mismatched display text and URL ("Click here" linking to suspicious domain)
  - Hidden text (white text on white background)
  - Excessive HTML (complex tables, deeply nested divs)

MODERATE RISK:
  - Large images (>500KB)
  - No plain-text alternative
  - Missing physical mailing address (required by CAN-SPAM)
  - No unsubscribe link (illegal in most jurisdictions)
```

### Technical Triggers

```
CRITICAL:
  - Failed SPF/DKIM/DMARC = almost guaranteed spam folder
  - Sending from free email domains (gmail.com, yahoo.com) via bulk sender
  - Sending from newly registered domain (<30 days old)
  - IP address on blacklists (check mxtoolbox.com)

IMPORTANT:
  - High bounce rate (>5%) = ISP penalizes future sends
  - High spam complaint rate (>0.1%) = reputation damage
  - Sending to purchased/scraped lists = blacklist risk
  - Inconsistent sending volume (0 emails for weeks, then 50K at once)
```

## List Hygiene

### Regular Cleaning Schedule

```
After every send:
  - Hard bounces: Remove immediately (invalid addresses)
  - Soft bounces: Mark, remove after 3 consecutive soft bounces

Monthly:
  - Remove addresses that haven't opened in 90 days
  - Re-verify addresses with high bounce risk (role-based: info@, admin@, team@)

Quarterly:
  - Run full list through email verification service (ZeroBounce, NeverBounce)
  - Remove spam trap indicators
  - Re-engagement campaign for 60-90 day inactive before removing
```

### Sunset Policy

```
Inactive for 30 days:  Reduce frequency (weekly → biweekly)
Inactive for 60 days:  Send re-engagement campaign (2-3 emails)
Inactive for 90 days:  Move to suppression list if no re-engagement
Inactive for 120 days: Remove from all active lists

"Inactive" = no opens AND no clicks. Track both -- some email clients block open tracking.
```

## Monitoring Deliverability

### Key Metrics to Watch

| Metric | Healthy | Warning | Critical |
|--------|---------|---------|----------|
| Inbox placement rate | >95% | 85-95% | <85% |
| Bounce rate | <2% | 2-5% | >5% |
| Spam complaint rate | <0.05% | 0.05-0.1% | >0.1% |
| Unsubscribe rate | <0.5% | 0.5-1% | >1% |
| Blacklist status | 0 listings | 1 minor | Any major (Spamhaus) |

### Tools for Monitoring

```
1. Google Postmaster Tools — reputation, delivery errors, spam rate for Gmail
2. Microsoft SNDS — delivery data for Outlook/Hotmail
3. MXToolbox — blacklist checks, DNS verification
4. mail-tester.com — send a test email, get deliverability score
5. Your ESP dashboard — bounce/complaint rates per send
```
