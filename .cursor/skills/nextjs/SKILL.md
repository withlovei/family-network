---
name: nextjs
description: Build and modify Next.js apps with App Router, React, TypeScript, and Tailwind. Use when working on Next.js projects, React components, pages, API routes, middleware, or when the user mentions Next.js, App Router, or frontend.
---

# Next.js Skill

## When to Use

Apply this skill when:
- Adding or editing pages, layouts, or components in a Next.js app
- Working with App Router (`app/`), `"use client"`, or Server Components
- Styling with Tailwind CSS
- Setting up API client, auth context, or middleware
- Defining or applying theme / design tokens for consistency
- Debugging hydration, routing, or build issues in Next.js

---

## Project Structure (Preferred)

```
src/
  app/              # App Router: layout.tsx, page.tsx, route segments, loading.tsx, error.tsx
  api/              # API client (axios instance), baseURL, interceptors
  components/       # Shared UI only (Header, Button, Card)
  contexts/         # React context (e.g. AuthContext)
  hooks/            # Custom hooks (useXxx)
  types/            # Shared TypeScript types/interfaces
  lib/              # (optional) Pure utils, constants, theme tokens
```

**Feature-based (for large features):** one folder per feature with `pages/`, `components/`, `hooks/`, `services/`, `types/`. Avoid a flat global `components/` for feature-specific UI.

**Management / scaling:**
- Use barrel exports (`index.ts`) per feature or folder only when they reduce noise; avoid deep re-exports.
- Keep shared types in `src/types/`; feature-specific types in the feature folder.
- Colocate tests next to modules or in `__tests__` at the same level.

---

## Theme & Design Consistency (High Priority)

**Single source of truth:** Define colors, spacing, and typography in one place so the app looks consistent and is easy to change (e.g. rebrand, dark mode).

1. **CSS variables + Tailwind `@theme` (e.g. Tailwind v4)**  
   In `globals.css` (or a dedicated theme file):
   - `:root`: define semantic tokens (`--background`, `--foreground`, `--primary`, `--muted`, `--border`, etc.).
   - `@theme inline { ... }`: map those to Tailwind theme (e.g. `--color-background`, `--color-foreground`) so components use `bg-background`, `text-foreground`.
   - Dark mode: use `@media (prefers-color-scheme: dark)` or a class like `.dark` and override the same variables so one set of class names works in both modes.

2. **Use theme tokens in components**  
   Prefer semantic tokens over raw palette:
   - Good: `bg-background`, `text-foreground`, `bg-primary`, `text-muted-foreground`, `border-border`.
   - Avoid: hardcoded `bg-slate-900`, `text-emerald-400` in many places (unless they are the defined tokens in theme).

3. **Fonts**  
   Define in root layout (e.g. `next/font`) and expose via CSS variables (e.g. `--font-sans`, `--font-mono`) and `@theme` so all pages use the same font stack.

4. **Spacing / radius**  
   If the project standardizes spacing, define in theme (e.g. `--radius-md`, `--spacing-page`) and use consistently; avoid magic numbers in class names when a token exists.

**When adding or changing UI:** always use the project’s theme tokens; if a new token is needed, add it to the central theme and then use it.

---

## App Router

- **Server Components** (default): no `"use client"`, no useState/useEffect; use for data fetch, SEO, and static content.
- **Client Components**: add `"use client"` at top when using state, effects, event handlers, or browser APIs.
- Layout: `layout.tsx` wraps segments; `page.tsx` is the route UI.
- Dynamic routes: `[id]/page.tsx`; params in Server Components via `props.params`, in Client via `useParams()`.
- Navigation: `<Link href="...">` for links; `useRouter()` from `next/navigation` for programmatic redirect.
- **Loading & error:** add `loading.tsx` for Suspense fallback and `error.tsx` for error boundary per segment when the route has async or fragile behavior.

---

## Components & TypeScript

- **Functional components only**, named in **PascalCase**; prefer arrow functions for consistency.
- Props: type with `interface` or `type`; **no `any`**.
- Prefer destructuring props; use optional chaining and `??` where appropriate.
- Hooks: use built-in (useState, useEffect, useMemo, useCallback); custom hooks in `hooks/`, name `useXxx`.
- Use `useEffect` only for side effects (subscriptions, syncing to storage); **avoid business logic in useEffect**.
- Keep components focused: extract sub-UIs into smaller components or hooks when logic or JSX grows.

---

## Styling (Tailwind)

- Use **Tailwind only**; avoid custom CSS unless necessary (e.g. complex animations or third-party overrides).
- **Class order:** layout → spacing → typography → color (and other visual properties). Keeps diffs readable and enforces consistency.
- Prefer **theme tokens** (e.g. `bg-background`, `text-foreground`) over raw colors for consistency and dark mode.
- Responsive: `sm:`, `md:`, `lg:` prefixes; **mobile-first**.

---

## API & Data

- Centralize API in `api/` or `services/`: **one axios (or fetch) instance** with baseURL and interceptors for auth (e.g. Bearer token) and 401 (clear storage, redirect to login).
- All API calls in **try/catch** with **user-friendly error messages** (no raw error stack in UI).
- Env: use `NEXT_PUBLIC_*` for client-exposed vars; read as `process.env.NEXT_PUBLIC_*`.
- Prefer typed responses: define response types in `types/` or feature `types/` and use them in API functions.

---

## Middleware

- File: `src/app/middleware.ts` or `middleware.ts` at src root.
- Export `middleware(request: NextRequest)`; return `NextResponse.next()` or `NextResponse.redirect()`.
- Use for **auth redirects** (e.g. protect `/dashboard`, redirect unauthenticated to `/login`); keep logic **light** (no heavy I/O).
- Matcher: `config.matcher` to limit which paths run middleware.

---

## Common Patterns

**Client form with submit:**  
`"use client"`; `useState` for fields and error; `useCallback` for submit handler; call API in try/catch; redirect on success (e.g. `router.push` + `router.refresh()`).

**Auth context:**  
Context holds `user`, `token`, `login`, `logout`, `isLoading`; persist token (e.g. localStorage + optional cookie for middleware); set cookie on login so middleware can redirect correctly.

**Protected page:**  
Middleware redirects unauthenticated users to login; page reads user from context or cookie/server if needed.

**Loading and error UX:**  
Use `loading.tsx` and `error.tsx` at route segment level; inside error boundary, show a clear message and optional retry instead of a blank or crashed screen.

---

## Best Practices for Experience & Maintainability

- **Consistency:** Use the same patterns for lists (e.g. loading skeleton, empty state, error state) across features.
- **Accessibility:** Prefer semantic HTML; use `aria-*` and keyboard support for custom controls; ensure focus and contrast for theme colors.
- **Performance:** Prefer Server Components; use Client only where needed; lazy-load heavy client components with `next/dynamic` when appropriate.
- **Workflow:** Follow project rule **workflow-plan-confirm**: plan and get confirmation before implementing non-trivial changes.

---

## Checklist Before Submitting

- [ ] Server vs Client component chosen correctly (`"use client"` only when needed)
- [ ] Props and state typed; no `any`
- [ ] **Theme:** Use project theme tokens (e.g. `bg-background`, `text-foreground`); no ad-hoc hardcoded colors unless they are the defined tokens
- [ ] Tailwind used; classes ordered (layout → spacing → typography → color)
- [ ] API calls in `api/` or `services/` with try/catch and user-friendly errors
- [ ] Links use `<Link>`; external links use `target="_blank"` and `rel="noopener noreferrer"` when appropriate
- [ ] Route has `loading.tsx` / `error.tsx` where async or error-prone behavior exists
