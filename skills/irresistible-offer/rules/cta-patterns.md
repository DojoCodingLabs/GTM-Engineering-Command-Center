# CTA Best Practices for Meta Ads

The Call to Action (CTA) button is the final conversion lever in your ad. Meta provides a fixed set of CTA types -- choosing the right one and pairing it with the right copy matters.

## CTA Type Decision Tree

```
Is the user paying money right now?
├── YES → Does the product cost >$50?
│   ├── YES → LEARN_MORE (reduce friction for high-ticket)
│   └── NO  → SHOP_NOW or GET_OFFER
└── NO  → What are they doing?
    ├── Creating an account → SIGN_UP
    ├── Starting a free trial → SIGN_UP or GET_OFFER
    ├── Downloading something → DOWNLOAD
    ├── Booking a call/demo → BOOK_TRAVEL (closest to "Book Now")
    ├── Watching/reading content → LEARN_MORE
    ├── Joining a waitlist → SIGN_UP
    └── Messaging you → SEND_MESSAGE or SEND_WHATSAPP_MESSAGE
```

## Meta CTA Types Reference

| CTA Value | Button Text | Best for |
|-----------|-------------|----------|
| `SIGN_UP` | Sign Up | Account creation, free trials, waitlists, newsletter |
| `LEARN_MORE` | Learn More | High-ticket products, complex offerings, content |
| `SHOP_NOW` | Shop Now | E-commerce, low-ticket direct purchase |
| `GET_OFFER` | Get Offer | Promotions, discounts, limited-time deals |
| `DOWNLOAD` | Download | Apps, ebooks, resources, lead magnets |
| `CONTACT_US` | Contact Us | Services, enterprise sales, custom solutions |
| `BOOK_TRAVEL` | Book Now | Appointments, demos, consultations |
| `SUBSCRIBE` | Subscribe | Recurring services, memberships |
| `APPLY_NOW` | Apply Now | Job applications, program admissions |
| `SEND_MESSAGE` | Send Message | Messenger-based lead gen |
| `SEND_WHATSAPP_MESSAGE` | WhatsApp | WhatsApp-based lead gen (strong in LATAM) |
| `WATCH_MORE` | Watch More | Video content, webinar funnels |
| `GET_QUOTE` | Get Quote | Insurance, custom pricing, B2B services |

## CTA Selection by Funnel Stage

### Top of Funnel (Awareness)
- **LEARN_MORE** -- Low commitment, educational content
- **WATCH_MORE** -- Video ads leading to webinars or video series
- Goal: get them to your site/content, not to convert yet

### Middle of Funnel (Consideration)
- **SIGN_UP** -- Free trial, waitlist, newsletter
- **DOWNLOAD** -- Lead magnet, ebook, toolkit
- **GET_OFFER** -- Special promotion to incentivize action
- Goal: capture their information

### Bottom of Funnel (Decision)
- **SHOP_NOW** -- Direct purchase for low-ticket
- **APPLY_NOW** -- Application-based programs (creates exclusivity)
- **SIGN_UP** -- Start free trial / create account
- Goal: conversion

### Retargeting
- **GET_OFFER** -- Discount or incentive for people who visited but didn't convert
- **SIGN_UP** -- Remind them to complete registration
- Goal: close the gap

## CTA Copy Pairing

The CTA button is fixed text from Meta, but you control the surrounding copy. The last line of your primary text should lead into the CTA button:

### SIGN_UP Pairings
```
"Join 2,400 developers who already leveled up."
[SIGN UP]

"Tu lugar en la proxima cohorte esta esperando."
[SIGN UP]

"Start your free 14-day trial. No credit card needed."
[SIGN UP]
```

### LEARN_MORE Pairings
```
"See how our graduates land jobs at top companies."
[LEARN MORE]

"Descubre el metodo que usan los mejores founders de LATAM."
[LEARN MORE]

"Watch the 3-minute demo to see it in action."
[LEARN MORE]
```

### GET_OFFER Pairings
```
"Claim your 40% early bird discount before Friday."
[GET OFFER]

"Aprovecha el precio de lanzamiento. Solo esta semana."
[GET OFFER]

"Get your free strategy call (valued at $200)."
[GET OFFER]
```

## LATAM-Specific CTA Considerations

### WhatsApp CTA
In LATAM markets, WhatsApp is often the highest-converting CTA:
- Users feel more comfortable messaging than filling forms
- Enables real-time conversation (higher close rate)
- Use `SEND_WHATSAPP_MESSAGE` for lead gen in CO, MX, BR, AR
- Requires a WhatsApp Business account connected to your page

### Language Considerations
- Meta shows the CTA button in the user's language automatically
- Your ad copy should lead into the CTA naturally in the same language
- In Spanish, the informal "tu" voice matches casual CTAs like "Registrate" (sign up)
- For professional audiences (enterprise, B2B), "usted" is appropriate: "Solicite su demo"

## CTA Testing Rules

1. **Test CTA types, not just copy**: SIGN_UP vs LEARN_MORE can differ by 40%+ in conversion rate
2. **Match CTA to landing page**: If CTA says "Sign Up," the landing page must have a signup form above the fold
3. **One CTA per ad**: Never confuse the user with multiple actions
4. **Mobile context**: 85%+ of Meta traffic is mobile. CTA must work with thumb-scroll behavior
5. **In Advantage+ Creative**: You can only set ONE `call_to_action_types` value per ad. Choose based on your primary conversion goal, not a mix

## Common CTA Mistakes

- **Using LEARN_MORE for everything** -- When you want signups, use SIGN_UP. LEARN_MORE signals "no commitment" which attracts browsers, not buyers
- **SHOP_NOW for high-ticket** -- Nobody shops for a $2,000 program. Use LEARN_MORE or APPLY_NOW
- **Mismatched landing page** -- CTA says "Get Offer" but landing page has no visible offer/discount
- **Ignoring WhatsApp in LATAM** -- In Colombia and Mexico, WhatsApp CTAs often outperform web forms by 2-3x
- **APPLY_NOW for simple products** -- Creates unnecessary friction. Reserve for cohort-based or exclusive programs
