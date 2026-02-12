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
- Debugging hydration, routing, or build issues in Next.js

## Project Structure (Preferred)

```
src/
  app/           # App Router: layout.tsx, page.tsx, route segments
  api/           # API client (axios/fetch), baseURL, interceptors
  components/    # Shared or feature components
  contexts/     # React context (e.g. AuthContext)
  hooks/        # Custom hooks (useXxx)
  types/        # TypeScript types/interfaces
```

Feature-based: per feature use `pages/`, `components/`, `hooks/`, `services/`, `types/` in one folder when the feature is large.

## App Router

- **Server Components** (default): no `"use client"`, no useState/useEffect; use for data fetch, SEO.
- **Client Components**: add `"use client"` at top when using state, effects, event handlers, or browser APIs.
- Layout: `layout.tsx` wraps segments; `page.tsx` is the route UI.
- Dynamic routes: `[id]/page.tsx`; params in Server Components via `props.params`, in Client via `useParams()`.
- Navigation: `<Link href="...">` for links; `useRouter()` from `next/navigation` for programmatic redirect.

## Components & TypeScript

- Prefer functional components; name in PascalCase.
- Props: type with `interface` or `type`; no `any`.
- Prefer destructuring props; optional chaining and `??` where useful.
- Hooks: use built-in (useState, useEffect, useMemo, useCallback); custom hooks in `hooks/`, name `useXxx`.
- Use `useEffect` only for side effects (subscriptions, syncing to storage); avoid business logic in useEffect.

## Styling (Tailwind)

- Use Tailwind classes only; avoid custom CSS unless necessary.
- Order classes: layout → spacing → typography → color.
- Responsive: `sm:`, `md:`, `lg:` prefixes; mobile-first.

## API & Data

- Centralize API in `api/` or `services/`: axios instance with baseURL, interceptors for auth (Bearer token) and 401 (e.g. clear storage, redirect to login).
- All API calls in try/catch; show user-friendly error messages.
- Env: use `NEXT_PUBLIC_*` for client-exposed vars; read in code as `process.env.NEXT_PUBLIC_*`.

## Middleware

- File: `src/app/middleware.ts` or `middleware.ts` at src root.
- Export `middleware(request: NextRequest)`; return `NextResponse.next()` or `NextResponse.redirect()`.
- Use for auth redirects (e.g. protect `/dashboard`, redirect unauthenticated to `/login`); keep logic light (no heavy I/O).
- Matcher: `config.matcher` to limit which paths run middleware.

## Common Patterns

**Client form with submit:**
- `"use client"`; `useState` for fields and error; `useCallback` for submit handler; call API in try/catch; redirect on success (e.g. `router.push` + `router.refresh()`).

**Auth context:**
- Context holds `user`, `token`, `login`, `logout`, `isLoading`; persist token (e.g. localStorage + optional cookie for middleware); set cookie on login so middleware can redirect correctly.

**Protected page:**
- Middleware redirects unauthenticated users to login; page reads user from context or cookie/server if needed.

## Checklist Before Submitting

- [ ] Server vs Client component chosen correctly (`"use client"` only when needed)
- [ ] Props and state typed; no `any`
- [ ] Tailwind used; classes ordered
- [ ] API calls in `api/` or `services/` with error handling
- [ ] Links use `<Link>`; external links use `target="_blank"` + `rel="noopener noreferrer"` when appropriate
