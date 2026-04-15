# Framework Detection -- Identifying Frontend and Backend Frameworks

## Why Framework Detection Matters for GTM

The framework determines:
- How tracking pixels are implemented (SPA vs MPA vs SSR)
- How landing pages are built (component system, routing)
- What SEO capabilities exist out of the box
- Where conversion tracking code goes
- How email templates are built
- Available build-time optimizations

## Frontend Framework Detection

### Next.js

```
Primary signals:
  - next.config.js or next.config.mjs or next.config.ts in root
  - "next" in package.json dependencies
  - app/ directory with layout.tsx and page.tsx (App Router)
  - pages/ directory with _app.tsx (Pages Router)

Secondary signals:
  - .next/ build directory
  - "next/image", "next/link", "next/script" imports
  - "use server" or "use client" directives in source
  - middleware.ts in root

Version detection:
  - App Router (layout.tsx, page.tsx, loading.tsx) → Next.js 13+
  - Pages Router only (_app.tsx, _document.tsx) → Next.js 12 or earlier
  - Both present → Migration in progress

GTM implications:
  - SSR/SSG: great for SEO out of the box
  - Server Components: tracking code must be in Client Components
  - Middleware: can handle redirects, A/B routing
  - API routes: can host CAPI endpoints
  - next/script: proper way to add tracking pixels
  - Image optimization: built-in (Core Web Vitals benefit)
```

### Vite + React

```
Primary signals:
  - vite.config.ts or vite.config.js in root
  - "vite" in package.json devDependencies
  - "react" and "react-dom" in package.json dependencies
  - index.html in root (not in public/)

Secondary signals:
  - src/main.tsx or src/main.jsx entry point
  - import.meta.env usage (Vite env variables)
  - VITE_ prefixed environment variables

Version detection:
  - Vite 5+ uses package.json "type": "module"
  - Check vite version in package.json

GTM implications:
  - SPA by default: poor SEO without prerendering
  - All tracking is client-side (no server components)
  - VITE_ prefix required for frontend env vars
  - Need vite-plugin-ssr or similar for SSR
  - Landing pages need prerendering for SEO
  - Tracking pixels go in index.html or root component
```

### Remix

```
Primary signals:
  - "@remix-run/react" in dependencies
  - "@remix-run/node" or "@remix-run/cloudflare" in dependencies
  - remix.config.js in root (Remix 1.x)
  - vite.config.ts with remix plugin (Remix 2+)

Secondary signals:
  - app/root.tsx entry point
  - app/routes/ directory with file-based routing
  - loader and action function exports

GTM implications:
  - SSR by default: good for SEO
  - Loaders run server-side (can host CAPI, data fetching)
  - Nested routing (shared layouts)
  - Progressive enhancement (forms work without JS)
  - Meta function for per-page SEO tags
```

### SvelteKit

```
Primary signals:
  - "@sveltejs/kit" in dependencies
  - "svelte" in dependencies
  - svelte.config.js in root

Secondary signals:
  - src/routes/ directory with +page.svelte files
  - src/app.html template
  - $app/ imports

GTM implications:
  - SSR by default: good for SEO
  - Smaller bundle sizes (compiler-based, not runtime)
  - +page.server.ts for server-side data loading
  - Built-in form actions
  - Adapter-based deployment (auto, node, static, cloudflare, etc.)
```

### Nuxt

```
Primary signals:
  - "nuxt" in dependencies
  - nuxt.config.ts or nuxt.config.js in root

Secondary signals:
  - pages/ directory with Vue SFC files
  - composables/ directory
  - server/ directory for API routes
  - .nuxt/ build directory

GTM implications:
  - SSR/SSG by default: good for SEO
  - Auto-imports for composables and components
  - Built-in useSeoMeta() for meta tags
  - Nitro server for API routes
  - Module ecosystem for analytics integration
```

### Astro

```
Primary signals:
  - "astro" in dependencies
  - astro.config.mjs or astro.config.ts in root

Secondary signals:
  - src/pages/ with .astro files
  - src/layouts/ directory
  - frontmatter (---) blocks in .astro files
  - Island architecture (client:load, client:visible directives)

GTM implications:
  - Static by default: excellent for SEO and performance
  - Zero JS shipped by default (great Core Web Vitals)
  - Islands for interactive components (tracking, forms)
  - Content collections for blog/docs (built-in)
  - Best framework for content-heavy, SEO-focused sites
```

### Angular

```
Primary signals:
  - "@angular/core" in dependencies
  - angular.json in root

Secondary signals:
  - src/app/app.component.ts
  - *.component.ts files
  - *.module.ts files (NgModule) or standalone components

GTM implications:
  - SPA by default (poor SEO without Angular Universal)
  - Zone.js can interfere with third-party scripts
  - Angular Universal for SSR (complex setup)
  - Heavy bundle sizes (consider impact on page speed)
```

## Backend Framework Detection

### Express.js

```
Primary signals:
  - "express" in dependencies
  - app.get(), app.post() patterns in source

GTM implications:
  - Can host CAPI endpoints
  - Middleware for tracking
  - No built-in SSR (need template engine)
```

### Django

```
Primary signals:
  - "django" in requirements.txt or Pipfile
  - settings.py with INSTALLED_APPS
  - manage.py in root

GTM implications:
  - Template-based SSR (good for SEO)
  - Django REST Framework for APIs
  - Built-in admin (useful for managing campaigns)
  - Can serve as CAPI endpoint host
```

### Rails

```
Primary signals:
  - "rails" in Gemfile
  - config/application.rb
  - app/controllers/ directory

GTM implications:
  - Server-rendered views (good for SEO)
  - Action Mailer for email
  - ActiveJob for background email sending
  - Hotwire/Turbo for SPA-like behavior with SSR SEO
```

### Laravel

```
Primary signals:
  - "laravel/framework" in composer.json
  - config/app.php
  - artisan in root

GTM implications:
  - Blade templates (SSR, good for SEO)
  - Laravel Mail for email
  - Queues for background processing
  - Cashier for Stripe integration (built-in)
```

## Monorepo Detection

```
Turborepo:
  - turbo.json in root
  - packages/ and apps/ directories
  - "turbo" in devDependencies

Nx:
  - nx.json in root
  - workspace.json or project.json files
  - "nx" in devDependencies

pnpm Workspaces:
  - pnpm-workspace.yaml in root
  - "workspaces" in package.json (also yarn/npm)

Lerna:
  - lerna.json in root

GTM implications for monorepos:
  - Landing page may be in a separate package (apps/marketing/)
  - Shared components may be in packages/ui/
  - Tracking code may need to be in a shared package
  - Build and deploy may be independent per app
  - Check which app handles the public-facing pages
```

## Package Manager Detection

```
npm:
  - package-lock.json in root
  - No other lockfile

yarn:
  - yarn.lock in root
  - Possibly .yarnrc.yml (Yarn Berry)

pnpm:
  - pnpm-lock.yaml in root
  - Possibly .npmrc with shamefully-hoist

bun:
  - bun.lockb in root

This matters for:
  - Install commands in CI/CD
  - Script execution (npx vs yarn vs pnpm exec vs bunx)
  - Workspace configuration
```

## Detection Output Format

After scanning, produce a structured detection result:

```json
{
  "framework": {
    "name": "Next.js",
    "version": "14.2.0",
    "variant": "App Router",
    "confidence": "confirmed"
  },
  "language": "TypeScript",
  "packageManager": "pnpm",
  "monorepo": false,
  "styling": {
    "primary": "Tailwind CSS",
    "componentLibrary": "shadcn/ui"
  },
  "rendering": {
    "strategy": "SSR + SSG hybrid",
    "seoReady": true
  },
  "hosting": {
    "detected": "Vercel",
    "confidence": "confirmed"
  }
}
```
