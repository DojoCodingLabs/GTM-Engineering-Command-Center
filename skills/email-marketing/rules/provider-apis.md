# Email Provider APIs -- Resend, SendGrid, Postmark

## Provider Selection Guide

| Feature | Resend | SendGrid | Postmark |
|---------|--------|----------|----------|
| Best for | Modern devs, React Email, startups | Scale, marketing + transactional | Transactional email, deliverability |
| Free tier | 100 emails/day, 3,000/month | 100 emails/day | 100 emails/month |
| Starting paid | $20/month (50K emails) | $19.95/month (50K emails) | $15/month (10K emails) |
| API style | REST, simple JSON | REST + SMTP, complex | REST + SMTP, clean |
| SDKs | Node, Python, Ruby, Go, Elixir, Java | Node, Python, Ruby, PHP, Go, Java, C# | Node, Python, Ruby, PHP, Java, .NET |
| Template engine | React Email (JSX) | Dynamic templates (Handlebars) | Mustache-like templates |
| Webhooks | Delivered, bounced, opened, clicked, complained | All events + 30+ event types | All events + inbound processing |
| DKIM setup | Automatic with domain verification | Manual DNS records | Automatic with domain verification |
| Best feature | Developer experience, React Email | Scale, marketing automation | Deliverability, message streams |
| Weakness | No marketing automation | Complex API, bloated | No marketing features |

## Detecting Which Provider Is in Use

### Package Detection

```
Resend:
  package.json: "resend" in dependencies
  Import: import { Resend } from 'resend'
  Env var: RESEND_API_KEY (starts with re_)

SendGrid:
  package.json: "@sendgrid/mail" in dependencies
  Import: import sgMail from '@sendgrid/mail'
  Env var: SENDGRID_API_KEY (starts with SG.)

Postmark:
  package.json: "postmark" in dependencies
  Import: import { ServerClient } from 'postmark'
  Env var: POSTMARK_SERVER_TOKEN or POSTMARK_API_TOKEN
```

## Resend API

### Setup

```typescript
import { Resend } from 'resend';

const resend = new Resend(process.env.RESEND_API_KEY);
```

### Send Single Email

```typescript
const { data, error } = await resend.emails.send({
  from: 'Juan <juan@dojocoding.com>',
  to: ['user@example.com'],
  subject: 'Welcome to Dojo Coding',
  html: '<h1>Welcome!</h1><p>Start your journey...</p>',
  // Or use React Email:
  // react: WelcomeEmail({ name: 'User' }),
  tags: [
    { name: 'category', value: 'welcome' },
    { name: 'campaign', value: 'onboarding-q2-2026' }
  ],
  headers: {
    'X-Entity-Ref-ID': 'unique-id-123'  // For deduplication
  }
});

if (error) {
  console.error('Resend error:', error);
  // error.statusCode, error.message, error.name
}
// data.id = email ID for tracking
```

### Send Batch Emails

```typescript
const { data, error } = await resend.batch.send([
  {
    from: 'Dojo <team@dojocoding.com>',
    to: ['user1@example.com'],
    subject: 'Your weekly digest',
    html: '<p>Digest for user 1...</p>'
  },
  {
    from: 'Dojo <team@dojocoding.com>',
    to: ['user2@example.com'],
    subject: 'Your weekly digest',
    html: '<p>Digest for user 2...</p>'
  }
]);
// Max 100 emails per batch call
```

### Domain Verification

```typescript
// List domains
const domains = await resend.domains.list();

// Add a domain
const { data } = await resend.domains.create({
  name: 'dojocoding.com'
});
// Returns DNS records to add (SPF, DKIM, MX for inbound)

// Verify domain (after adding DNS records)
await resend.domains.verify(domainId);
```

### Webhooks

```typescript
// Resend webhook events
type ResendWebhookEvent =
  | 'email.sent'           // Email accepted by Resend
  | 'email.delivered'      // Delivered to recipient's server
  | 'email.delivery_delayed' // Temporary delivery issue
  | 'email.bounced'        // Hard bounce (remove address)
  | 'email.complained'     // Marked as spam (suppress immediately)
  | 'email.opened'         // Email opened (pixel tracking)
  | 'email.clicked';       // Link clicked

// Webhook verification
import { Webhook } from 'svix';

const wh = new Webhook(process.env.RESEND_WEBHOOK_SECRET);
const payload = wh.verify(body, headers);
```

## SendGrid API

### Setup

```typescript
import sgMail from '@sendgrid/mail';

sgMail.setApiKey(process.env.SENDGRID_API_KEY);
```

### Send Single Email

```typescript
const msg = {
  to: 'user@example.com',
  from: {
    email: 'team@dojocoding.com',
    name: 'Dojo Coding'
  },
  subject: 'Welcome to Dojo Coding',
  text: 'Plain text version',
  html: '<h1>Welcome!</h1>',
  categories: ['welcome', 'onboarding'],
  customArgs: {
    campaign: 'onboarding-q2-2026',
    userId: 'user-123'
  },
  trackingSettings: {
    clickTracking: { enable: true },
    openTracking: { enable: true },
    subscriptionTracking: { enable: false }  // Use your own unsubscribe
  }
};

try {
  const [response] = await sgMail.send(msg);
  // response.statusCode === 202 = accepted
  // response.headers['x-message-id'] = tracking ID
} catch (error) {
  // error.code, error.response.body.errors
}
```

### Dynamic Templates

```typescript
const msg = {
  to: 'user@example.com',
  from: 'team@dojocoding.com',
  templateId: 'd-XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX',
  dynamicTemplateData: {
    first_name: 'Maria',
    product_name: 'Blockchain Fundamentals',
    trial_days_remaining: 5,
    upgrade_url: 'https://dojocoding.com/upgrade'
  }
};

await sgMail.send(msg);
```

### Contact Lists (Marketing)

```typescript
import client from '@sendgrid/client';

client.setApiKey(process.env.SENDGRID_API_KEY);

// Add contact to list
const [response] = await client.request({
  method: 'PUT',
  url: '/v3/marketing/contacts',
  body: {
    list_ids: ['list-id-xxx'],
    contacts: [{
      email: 'user@example.com',
      first_name: 'Maria',
      custom_fields: {
        plan: 'trial',
        signup_source: 'meta_ads'
      }
    }]
  }
});
```

## Postmark API

### Setup

```typescript
import { ServerClient } from 'postmark';

const client = new ServerClient(process.env.POSTMARK_SERVER_TOKEN);
```

### Send Single Email

```typescript
const response = await client.sendEmail({
  From: 'team@dojocoding.com',
  To: 'user@example.com',
  Subject: 'Welcome to Dojo Coding',
  HtmlBody: '<h1>Welcome!</h1>',
  TextBody: 'Welcome!',
  Tag: 'welcome-sequence',
  TrackOpens: true,
  TrackLinks: 'HtmlAndText',
  MessageStream: 'outbound',  // or 'broadcast' for marketing
  Metadata: {
    campaign: 'onboarding-q2-2026',
    userId: 'user-123'
  }
});

// response.MessageID = tracking ID
// response.SubmittedAt = timestamp
// response.ErrorCode = 0 means success
```

### Message Streams

Postmark enforces separation of transactional and marketing email:

```typescript
// Transactional (default stream)
{ MessageStream: 'outbound' }
// Receipts, password resets, account notifications

// Marketing (broadcast stream)
{ MessageStream: 'broadcast' }
// Newsletters, promotions, drip sequences
// Requires List-Unsubscribe header

// Each stream has separate IP/reputation
// This protects transactional delivery from marketing complaints
```

### Templates

```typescript
// Send with template
const response = await client.sendEmailWithTemplate({
  From: 'team@dojocoding.com',
  To: 'user@example.com',
  TemplateAlias: 'welcome',
  TemplateModel: {
    name: 'Maria',
    product: 'Blockchain Fundamentals',
    action_url: 'https://dojocoding.com/start'
  },
  MessageStream: 'outbound'
});
```

## Error Handling Across Providers

```typescript
// Universal error handling pattern
async function sendEmail(provider: 'resend' | 'sendgrid' | 'postmark', params: EmailParams) {
  try {
    switch (provider) {
      case 'resend': {
        const { error } = await resend.emails.send(params);
        if (error) throw new Error(`Resend: ${error.message} (${error.statusCode})`);
        break;
      }
      case 'sendgrid': {
        await sgMail.send(params);
        break;
      }
      case 'postmark': {
        const result = await postmark.sendEmail(params);
        if (result.ErrorCode !== 0) throw new Error(`Postmark: ${result.Message}`);
        break;
      }
    }
  } catch (err) {
    // Common retry-worthy errors:
    //   429 (rate limited) → retry with exponential backoff
    //   500/502/503 (server error) → retry up to 3 times
    //   422 (invalid params) → do not retry, fix the request
    //   401 (auth) → do not retry, fix API key
    //   Hard bounce → do not retry, suppress the address
  }
}
```

## Rate Limits

| Provider | Sends/Second | Daily Limit | Batch Size |
|----------|-------------|------------|------------|
| Resend (free) | 2/sec | 100/day | 100/batch |
| Resend (paid) | 10/sec | Based on plan | 100/batch |
| SendGrid (free) | 100/sec | 100/day | 1,000/batch |
| SendGrid (paid) | 100/sec | Based on plan | 1,000/batch |
| Postmark (any) | 50/sec | No hard limit | 500/batch |
