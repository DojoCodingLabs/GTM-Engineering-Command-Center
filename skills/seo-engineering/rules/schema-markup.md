# Schema Markup -- JSON-LD for SaaS, Education, and Content Sites

## JSON-LD Fundamentals

JSON-LD is the recommended format for structured data. It is embedded in a script tag of type application/ld+json in the page head and does not affect visual rendering.

```html
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "Organization",
  "name": "Dojo Coding",
  "url": "https://dojocoding.com"
}
</script>
```

### Why JSON-LD Over Microdata or RDFa

- Separate from HTML (does not clutter markup)
- Easier to generate server-side
- Google prefers JSON-LD
- Can describe entities not visible on the page
- Easy to add/remove without affecting page layout

## Essential Schema Types for SaaS

### Organization Schema (Homepage)

```json
{
  "@context": "https://schema.org",
  "@type": "Organization",
  "name": "Dojo Coding",
  "alternateName": "Dojo Coding Labs",
  "url": "https://dojocoding.com",
  "logo": {
    "@type": "ImageObject",
    "url": "https://dojocoding.com/logo.png",
    "width": 512,
    "height": 512
  },
  "description": "Project-based coding education platform for blockchain and Web3 developers",
  "foundingDate": "2024",
  "founders": [
    {
      "@type": "Person",
      "name": "Founder Name"
    }
  ],
  "address": {
    "@type": "PostalAddress",
    "addressCountry": "CO"
  },
  "sameAs": [
    "https://twitter.com/dojocoding",
    "https://github.com/DojoCodingLabs",
    "https://linkedin.com/company/dojocoding",
    "https://discord.gg/dojocoding"
  ],
  "contactPoint": {
    "@type": "ContactPoint",
    "contactType": "customer support",
    "email": "support@dojocoding.com",
    "availableLanguage": ["English", "Spanish"]
  }
}
```

### Product/SoftwareApplication Schema (Product Pages)

```json
{
  "@context": "https://schema.org",
  "@type": "SoftwareApplication",
  "name": "Dojo Coding Platform",
  "description": "Learn blockchain development through project-based courses, mentorship, and community.",
  "applicationCategory": "EducationalApplication",
  "operatingSystem": "Web",
  "url": "https://dojocoding.com",
  "screenshot": "https://dojocoding.com/images/platform-screenshot.png",
  "offers": [
    {
      "@type": "Offer",
      "name": "Free Tier",
      "price": "0",
      "priceCurrency": "USD",
      "description": "Access to free courses and community"
    },
    {
      "@type": "Offer",
      "name": "Pro",
      "price": "29.99",
      "priceCurrency": "USD",
      "billingIncrement": "P1M",
      "description": "Full access to all courses, projects, and mentorship"
    }
  ],
  "aggregateRating": {
    "@type": "AggregateRating",
    "ratingValue": "4.8",
    "reviewCount": "342",
    "bestRating": "5"
  }
}
```

### Course Schema (Course Pages)

```json
{
  "@context": "https://schema.org",
  "@type": "Course",
  "name": "Blockchain Fundamentals",
  "description": "Learn the foundations of blockchain technology, from consensus mechanisms to smart contract development.",
  "url": "https://dojocoding.com/courses/blockchain-fundamentals",
  "provider": {
    "@type": "Organization",
    "name": "Dojo Coding",
    "url": "https://dojocoding.com"
  },
  "educationalLevel": "Beginner",
  "inLanguage": "en",
  "coursePrerequisites": "Basic programming knowledge (any language)",
  "numberOfCredits": "0",
  "timeRequired": "PT40H",
  "hasCourseInstance": {
    "@type": "CourseInstance",
    "courseMode": "online",
    "courseSchedule": {
      "@type": "Schedule",
      "repeatFrequency": "P1W",
      "repeatCount": "8"
    }
  },
  "offers": {
    "@type": "Offer",
    "category": "Paid",
    "price": "29.99",
    "priceCurrency": "USD"
  },
  "image": "https://dojocoding.com/images/courses/blockchain-fundamentals.png"
}
```

### FAQ Schema (Any Page with FAQ Section)

```json
{
  "@context": "https://schema.org",
  "@type": "FAQPage",
  "mainEntity": [
    {
      "@type": "Question",
      "name": "Do I need prior blockchain experience?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "No. Our courses start from the fundamentals. Basic programming knowledge in any language is the only prerequisite."
      }
    },
    {
      "@type": "Question",
      "name": "How long does the program take?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "The core Blockchain Fundamentals course takes 8 weeks at 5 hours per week. The full developer track takes 6 months."
      }
    },
    {
      "@type": "Question",
      "name": "Is there a free trial?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "Yes. You get 14 days of full access to all courses and features. No credit card required to start."
      }
    }
  ]
}
```

### BreadcrumbList Schema (Navigation)

```json
{
  "@context": "https://schema.org",
  "@type": "BreadcrumbList",
  "itemListElement": [
    {
      "@type": "ListItem",
      "position": 1,
      "name": "Home",
      "item": "https://dojocoding.com"
    },
    {
      "@type": "ListItem",
      "position": 2,
      "name": "Courses",
      "item": "https://dojocoding.com/courses"
    },
    {
      "@type": "ListItem",
      "position": 3,
      "name": "Blockchain Fundamentals",
      "item": "https://dojocoding.com/courses/blockchain-fundamentals"
    }
  ]
}
```

### Article/BlogPosting Schema (Blog Posts)

```json
{
  "@context": "https://schema.org",
  "@type": "BlogPosting",
  "headline": "How to Build Your First Smart Contract in Solidity",
  "description": "Step-by-step guide to writing, testing, and deploying your first Solidity smart contract on Ethereum.",
  "url": "https://dojocoding.com/blog/first-smart-contract-solidity",
  "datePublished": "2026-04-01T10:00:00-05:00",
  "dateModified": "2026-04-10T14:30:00-05:00",
  "author": {
    "@type": "Person",
    "name": "Author Name",
    "url": "https://dojocoding.com/team/author-name"
  },
  "publisher": {
    "@type": "Organization",
    "name": "Dojo Coding",
    "logo": {
      "@type": "ImageObject",
      "url": "https://dojocoding.com/logo.png"
    }
  },
  "image": {
    "@type": "ImageObject",
    "url": "https://dojocoding.com/images/blog/first-smart-contract.png",
    "width": 1200,
    "height": 628
  },
  "wordCount": 2500,
  "keywords": ["solidity", "smart contract", "ethereum", "tutorial"],
  "mainEntityOfPage": {
    "@type": "WebPage",
    "@id": "https://dojocoding.com/blog/first-smart-contract-solidity"
  }
}
```

### HowTo Schema (Tutorial Pages)

```json
{
  "@context": "https://schema.org",
  "@type": "HowTo",
  "name": "How to Deploy a Smart Contract to Ethereum",
  "description": "Complete guide to deploying your Solidity smart contract to Ethereum mainnet using Hardhat.",
  "totalTime": "PT30M",
  "estimatedCost": {
    "@type": "MonetaryAmount",
    "currency": "USD",
    "value": "5"
  },
  "tool": [
    { "@type": "HowToTool", "name": "Node.js (v18+)" },
    { "@type": "HowToTool", "name": "Hardhat" },
    { "@type": "HowToTool", "name": "MetaMask wallet" }
  ],
  "step": [
    {
      "@type": "HowToStep",
      "name": "Install Hardhat",
      "text": "Run npm install --save-dev hardhat in your project directory.",
      "url": "https://dojocoding.com/blog/deploy-smart-contract#step-1"
    },
    {
      "@type": "HowToStep",
      "name": "Write the Contract",
      "text": "Create a new Solidity file in the contracts/ directory with your smart contract code.",
      "url": "https://dojocoding.com/blog/deploy-smart-contract#step-2"
    },
    {
      "@type": "HowToStep",
      "name": "Configure Network",
      "text": "Add your Ethereum mainnet RPC URL and private key to hardhat.config.js.",
      "url": "https://dojocoding.com/blog/deploy-smart-contract#step-3"
    },
    {
      "@type": "HowToStep",
      "name": "Deploy",
      "text": "Run npx hardhat run scripts/deploy.js --network mainnet to deploy your contract.",
      "url": "https://dojocoding.com/blog/deploy-smart-contract#step-4"
    }
  ]
}
```

## Implementation Patterns

### Next.js App Router

```typescript
// app/layout.tsx or page.tsx
// Build the JSON-LD object, then render it in a script tag.
// Use the built-in Next.js Script component or a standard script element.
export default function Page() {
  const jsonLd = {
    '@context': 'https://schema.org',
    '@type': 'Organization',
    name: 'Dojo Coding',
    url: 'https://dojocoding.com',
  };

  return (
    <>
      <script
        type="application/ld+json"
        // Pass the serialized JSON as the inner content.
        // In Next.js, use the standard pattern for injecting raw HTML in script tags.
        // The content is static JSON with no user input, so XSS risk is zero.
        children={JSON.stringify(jsonLd)}
      />
      {/* Page content */}
    </>
  );
}
```

### Vite/React SPA

```typescript
// Use react-helmet-async or a custom Head component
import { Helmet } from 'react-helmet-async';

function CoursePage({ course }) {
  const jsonLd = {
    '@context': 'https://schema.org',
    '@type': 'Course',
    name: course.name,
    description: course.description,
  };

  return (
    <>
      <Helmet>
        <script type="application/ld+json">{JSON.stringify(jsonLd)}</script>
      </Helmet>
      {/* Page content */}
    </>
  );
}
```

### Multiple Schema Types on One Page

You can include multiple schema blocks on a single page. Each is a separate script tag. Google processes all of them.

```
Page: /courses/blockchain-fundamentals

Schema blocks:
  1. Organization (site-wide, in layout)
  2. BreadcrumbList (Home > Courses > Blockchain Fundamentals)
  3. Course (details about this specific course)
  4. FAQPage (FAQ section at the bottom)
```

## Validation Checklist

```
Before deploying schema:
  [ ] Valid JSON (no trailing commas, proper quotes)
  [ ] All required fields present for the schema type
  [ ] URLs are absolute (https://..., not relative /path)
  [ ] Dates in ISO 8601 format (2026-04-14T10:00:00-05:00)
  [ ] Images are accessible (not behind auth, not 404)
  [ ] Prices match actual pricing on the page
  [ ] Test with Google Rich Results Test
  [ ] Test with Schema.org Validator
  [ ] Check Google Search Console after deployment for errors
```
