# Design System Integration -- Detecting and Using a Project's Existing Components

## Why This Matters

When building or modifying landing pages, you must use the project's existing design system. Creating custom CSS or importing random component libraries causes:
- Visual inconsistency (looks broken)
- Maintenance burden (two systems to update)
- Bundle size increase (duplicate component code)
- Design review failures

## Design System Detection Process

### Step 1: Identify the Component Library

Check these locations in order:

```
1. Package.json dependencies:
   - "@radix-ui/react-*" → Radix primitives (often under shadcn/ui)
   - "@headlessui/react" → Headless UI (Tailwind Labs)
   - "@chakra-ui/react" → Chakra UI
   - "@mantine/core" → Mantine
   - "antd" → Ant Design
   - "@mui/material" → Material UI
   - "daisyui" → DaisyUI (Tailwind plugin)
   - Custom DS → check src/components/ui/ or src/design-system/

2. UI component directory:
   - src/components/ui/ → Custom DS or shadcn/ui
   - src/components/common/ → Custom DS
   - src/design-system/ → Dedicated DS package
   - Check for index.ts barrel exports (indicates structured DS)

3. Tailwind config:
   - tailwind.config.js/ts → Custom tokens, colors, typography
   - Look for theme.extend.colors, theme.extend.fontFamily
   - Custom design tokens indicate a mature DS

4. CSS variables:
   - src/index.css or src/globals.css → CSS custom properties
   - :root { --primary: ...; --background: ...; }
   - Indicates a token-based design system
```

### Step 2: Understand Import Patterns

```
Once you find the DS, identify how components are imported:

Barrel import pattern (preferred):
  import { Button, Card, Input } from '@/components/ui';
  → Use this pattern. Never import individual files.

Direct import pattern:
  import { Button } from '@/components/ui/button';
  → Use this only if there's no barrel export.

Namespaced import:
  import * as UI from '@/components/ui';
  → Rare, but respect it if the codebase uses it.

Check 3-5 existing page files to see the import pattern in use.
DO NOT introduce a new import pattern. Follow what exists.
```

### Step 3: Map Available Components

Create a mental inventory of what's available before coding:

```
Layout components:
  - Container/Wrapper: max-width, padding, centering
  - Card/Panel: bordered content areas
  - Grid/Flex: layout primitives
  - Section: page sections with consistent spacing
  - Separator/Divider: visual breaks

Typography:
  - Heading levels (H1-H6 or display-1 through display-6)
  - Body text sizes
  - Special text (code, label, caption)

Interactive:
  - Button (variants: primary, secondary, ghost, destructive)
  - Link (styled anchor)
  - Input, Select, Textarea
  - Tabs, Accordion

Feedback:
  - Alert, Toast, Badge/Pill
  - Loading spinner, Skeleton
  - Progress bar

Overlay:
  - Dialog/Modal, Sheet, Popover
  - Dropdown, Tooltip
```

## Building Landing Pages with an Existing DS

### Pattern: Extending Without Breaking

When the DS doesn't have a specific landing page component, compose from existing primitives:

```typescript
// GOOD: Compose from existing components
import { Button, Card, CardContent } from '@/components/ui';

function HeroSection() {
  return (
    <section className="py-16 px-4 sm:py-24 text-center">
      <h1 className="text-dojo-display-1 font-bold mb-4">
        Ship Smart Contracts 10x Faster
      </h1>
      <p className="text-dojo-display-7 text-dojo-text-secondary mb-8 max-w-2xl mx-auto">
        The only platform that takes you from zero to deployed in 30 days.
      </p>
      <Button variant="primary" size="lg">
        Start My Free Trial
      </Button>
    </section>
  );
}

// BAD: Custom CSS that ignores the DS
function HeroSection() {
  return (
    <section style={{ padding: '100px 20px', textAlign: 'center' }}>
      <h1 style={{ fontSize: '48px', fontWeight: 'bold', color: '#C980FC' }}>
        Ship Smart Contracts 10x Faster
      </h1>
      <button style={{
        backgroundColor: '#C980FC',
        color: 'white',
        padding: '12px 24px',
        borderRadius: '8px'
      }}>
        Start Free Trial
      </button>
    </section>
  );
}
```

### When the DS Is Missing a Component

Sometimes landing pages need components the DS doesn't provide. The decision tree:

```
Do you need this component in more than one place?
├── Yes → Create it as a proper DS component (add to src/components/ui/)
│         Get design review/approval first. Follow DS patterns exactly.
└── No → Create it as a page-level component using DS primitives
          Use DS tokens (colors, spacing, typography) even for custom layouts
          Document it for future extraction if it's reused later
```

### Landing Page vs Dashboard Components

Many projects have separate visual languages for marketing pages and the authenticated app. Detect which you're building for:

```
Landing/Marketing pages:
  - Public routes (/, /pricing, /about, /blog)
  - Often use different background, typography, and spacing
  - May have their own component set (src/components/landing/)
  - Glassmorphism, gradients, large type, more visual flair

Dashboard/App pages:
  - Authenticated routes (/dashboard, /settings, /courses)
  - Standard DS components from src/components/ui/
  - Consistent, functional design
  - Data-dense, interactive
```

### Token Usage

Always use design tokens, never hardcoded values:

```typescript
// GOOD: Using project tokens
className="bg-dojo-primary-lilac text-white rounded-dojo-lg p-4"
className="text-dojo-display-3 font-bold"
className="bg-dojo-background-01 border-dojo-background-04"

// BAD: Hardcoded values
className="bg-[#C980FC] text-white rounded-lg p-4"
style={{ color: '#C980FC' }}
style={{ fontSize: '2.25rem' }}
```

### Responsive Patterns

Follow the project's responsive conventions:

```typescript
// Check how the project handles responsive design:

// Tailwind breakpoints (most common):
className="text-sm sm:text-base lg:text-lg"
className="grid-cols-1 sm:grid-cols-2 lg:grid-cols-3"

// CSS modules with media queries:
// Check existing .module.css files for the pattern

// JS-based responsive:
const { isMobile } = useViewportState();
// Check for hooks like useMediaQuery, useViewportState, useBreakpoint

// Follow whichever pattern the project already uses.
```

## Integration Checklist

Before building a landing page in an existing project:

```
Discovery:
  [ ] Identified the component library/DS
  [ ] Documented available components (layout, typography, interactive, feedback)
  [ ] Found the import pattern (barrel vs direct)
  [ ] Identified design tokens (colors, spacing, typography classes)
  [ ] Checked for landing-specific components (src/components/landing/)
  [ ] Identified the responsive pattern (Tailwind breakpoints, CSS modules, JS hooks)

Building:
  [ ] Every button uses the DS Button component (with correct variant)
  [ ] Every card/container uses the DS Card component
  [ ] All colors from design tokens (no hardcoded hex values)
  [ ] All typography from design tokens (no arbitrary font sizes)
  [ ] All spacing using Tailwind classes or DS spacing tokens
  [ ] No custom CSS that duplicates existing DS functionality
  [ ] Responsive design follows project conventions

Verification:
  [ ] Visual consistency with the rest of the site
  [ ] No new npm dependencies added for UI components
  [ ] Import pattern matches existing codebase
  [ ] Mobile layout tested at 375px
  [ ] Dark mode works (if the project supports it)
```

## Common DS Pitfalls

```
1. Importing a new component library when one exists
   "I'll just use Material UI for this one button"
   → Now you have 2 component libraries. Don't.

2. Using arbitrary Tailwind values instead of tokens
   className="bg-[#C980FC]" instead of className="bg-dojo-primary-lilac"
   → Breaks if the brand color changes. Always use tokens.

3. Skipping the barrel export
   import { Button } from '@/components/ui/button';
   → When the project uses: import { Button } from '@/components/ui';

4. Creating a "utils.css" for landing page styles
   → Use Tailwind utilities or extend the DS. Don't create a parallel style system.

5. Copying a component from another project
   → The copied component won't match. Rebuild using local DS primitives.
```
