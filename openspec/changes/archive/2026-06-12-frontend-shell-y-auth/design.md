## Context

The project has a fully functional backend (C-01 to C-20) with auth endpoints (C-03: JWT + 2FA + password recovery) and RBAC (C-04). All backend communication must go through a single centralized HTTP client that handles JWT attachment and transparent token refresh. The frontend is a new greenfield React SPA — no legacy code, framework decisions, or migration constraints. Identity and tenant come exclusively from the authenticated session (no URL param, form field, or header can override who the user is).

## Goals / Non-Goals

**Goals:**
- Scaffold `frontend/` with React 18 + TypeScript + Vite, Tailwind CSS, TanStack Query, React Hook Form + Zod, Axios
- Centralized Axios instance: request interceptor attaches JWT Bearer token; response interceptor catches 401, transparently refreshes via `POST /api/auth/refresh`, retries original request, redirects to login on refresh failure
- AuthContext that manages access token, refresh token, current user (with roles/permissions from `GET /api/auth/me`), and exposes `login()`, `logout()`, `isAuthenticated`, `user`
- Login, 2FA, Forgot Password, Reset Password screens consuming C-03 endpoints
- ProtectedRoute component: redirects to login if unauthenticated, renders fallback if missing required permission
- Layout component with sidebar menu adapted to session permissions
- Vitest + React Testing Library tests covering login render, auth flow (mocked API), guard redirects, transparent refresh

**Non-Goals:**
- Feature pages beyond auth and shell (deferred to subsequent changes)
- E2E tests (unit + integration within Vitest/RTL scope only)
- Dark mode or theme customization
- i18n (deferred, use hardcoded strings)
- Storybook or component documentation
- PWAs, SSR, or code splitting (lazy load routes only)

## Decisions

1. **Feature-based folder structure**: `frontend/src/{features/<name>, shared/<type>}`. Each feature groups its own pages, components, hooks, services, and types. Shared code (http client, types, reusable components) lives in `shared/`. This follows the established architecture from knowledge-base/08_arquitectura_propuesta.md §2. Alternatives considered: flat pages/ (doesn't scale horizontally) and modules/ (same idea, different name).

2. **Vite over CRA or Next.js**: CRA is deprecated, Next.js adds SSR/routing complexity this SPA doesn't need. Vite provides instant HMR, native ESM, and the simplest React 18 setup. The project needs a pure SPA — no SSR, no static generation.

3. **Axios over fetch**: TanStack Query works natively with fetch but Axios provides interceptors (the core mechanism for transparent token refresh), better error handling, and configurable instances. The centralized `apiClient` wraps Axios with auth interceptors. No direct Axios usage outside `shared/services/httpClient.ts` — feature services import `apiClient` and add their own endpoint methods.

4. **AuthContext over Zustand/Redux for session state**: Auth is read-heavy (check on every route transition) and write-light (login/logout). React Context is sufficient and avoids extra dependencies. The context holds `{ user, accessToken, isAuthenticated, isRefreshing, login(), logout() }`. Tokens are stored in memory (context) + localStorage for hard refresh recovery. A `GET /api/auth/me` call on app boot restores the session from the stored refresh token.

5. **TanStack Query for API calls**: All data fetching goes through `useQuery`/`useMutation` hooks. Auth calls (login, logout) bypass the query cache (they're write-only mutations). The HTTP client interceptors handle token logic transparently — TanStack Query is unaware of auth.

6. **Route guard as `ProtectedRoute` component**: A wrapper around `<Route>` or `<Outlet>` that checks `AuthContext.isAuthenticated` and optional `requiredPermissions`. If not authenticated → redirect to `/login`. If authenticated but missing permissions → render a "not authorized" fallback (not a redirect to avoid redirect loops). Permission checking is synchronous (permissions are loaded into context from `GET /api/auth/me` on boot).

7. **React Hook Form + Zod for forms**: Login and recovery forms use React Hook Form for performant form state with `@hookform/resolvers/zod` for schema-based validation. Each form has a corresponding Zod schema (email, password length, TOTP code format). Error messages from the backend (e.g., "invalid credentials") are surfaced via form-level `setError()`.

8. **Token refresh flow**: On 401, the response interceptor (a) checks if a refresh is already in progress (lock via a promise singleton to prevent race conditions), (b) calls `POST /api/auth/refresh` with the stored refresh token, (c) updates tokens in context + localStorage, (d) retries the original request with the new access token. If refresh fails (401, network error), clears session and redirects to login.

9. **Layout with permission-aware sidebar**: The `Layout` component wraps all authenticated pages. It reads `user.permissions` from context to render menu items. The sidebar is a collapsible vertical nav with sections matching feature modules. Each menu item declares a `requiredPermission` — if the user lacks it, the item is hidden. This is NOT a security boundary (permissions are enforced server-side), only UX.

## Risks / Trade-offs

- **[Risk] Token in localStorage is XSS-accessible** → Storage in memory + localStorage is a pragmatic trade-off. An HttpOnly cookie would require a BFF or server-side rendering which is out of scope. Mitigation: the access token is short-lived (15min), the refresh token has rotation, and a CSRF-like pattern is infeasible in SPA without BFF. Acceptable for MVP.
- **[Risk] Multiple parallel 401s trigger concurrent refreshes** → The promise singleton pattern in the response interceptor queues concurrent 401s onto a single refresh call. All queued requests retry with the new token. Mitigation: implemented as a shared promise reference (`let refreshPromise: Promise<void> | null = null`).
- **[Risk] Race condition on app boot (token restored but user not yet loaded)** → The `AuthProvider` initializes in a "loading" state. During loading, the `ProtectedRoute` renders a spinner instead of redirecting. Once user is loaded (or refresh fails), loading resolves and routing works normally.
- **[Trade-off] Monorepo without npm workspaces** → `frontend/` has its own `package.json` and dependencies. No shared tsconfig or npm workspaces with `backend/`. Keeps concerns fully separated. A shared types package could be extracted later if API types drift becomes painful.
- **[Trade-off] No BFF / backend-for-frontend** → All auth token logic lives in the client-side Axios interceptor. A BFF could use HttpOnly cookies and eliminate XSS token exposure. Deferred because it adds a deployment artifact and server-side rendering overhead.
