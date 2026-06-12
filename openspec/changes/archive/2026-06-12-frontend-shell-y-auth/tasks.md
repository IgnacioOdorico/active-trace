## 1. Scaffold & Dependencies

- [x] 1.1 Create `frontend/` directory and scaffold with Vite (`npm create vite@latest frontend -- --template react-ts`)
- [x] 1.2 Install dependencies: `react-router-dom`, `@tanstack/react-query`, `axios`, `react-hook-form`, `@hookform/resolvers`, `zod`, `tailwindcss`, `postcss`, `autoprefixer`, `vitest`, `@testing-library/react`, `@testing-library/jest-dom`, `@testing-library/user-event`, `jsdom`, `@types/react`, `@types/react-dom`
- [x] 1.3 Configure Tailwind CSS (`tailwind.config.js`, `postcss.config.js`, `@tailwind` directives in index.css)
- [x] 1.4 Configure Vitest in `vite.config.ts` with `jsdom` environment and setup file
- [x] 1.5 Create feature-based folder structure: `frontend/src/{features/{auth,shell},shared/{components,hooks,services,types,pages}}`
- [x] 1.6 Create `frontend/src/App.tsx` with React Router and TanStack Query Provider wrapping
- [x] 1.7 Create `frontend/src/main.tsx` entry point rendering App

## 2. Centralized HTTP Client

- [x] 2.1 Create `frontend/src/shared/services/httpClient.ts` — Axios instance with `baseURL` from env
- [x] 2.2 Implement request interceptor that attaches `Authorization: Bearer <token>` from AuthContext
- [x] 2.3 Implement response interceptor that catches 401, acquires refresh lock promise singleton, calls `POST /api/auth/refresh`, updates tokens, retries original request
- [x] 2.4 Implement refresh failure handling: clear session, redirect to `/login`
- [x] 2.5 Implement logout guard: when user explicitly logs out, skip refresh attempts on subsequent 401s

## 3. Auth Types & Zod Schemas

- [x] 3.1 Create `frontend/src/features/auth/types.ts` — `LoginRequest`, `LoginResponse`, `TwoFactorVerify`, `ForgotPasswordRequest`, `ResetPasswordRequest`, `AuthUser` (id, email, roles, permissions, tenant_id)
- [x] 3.2 Create `frontend/src/features/auth/schemas.ts` — Zod schemas for login (email, password min 8), TOTP (6 digits), forgot password (email), reset password (password + confirm match)
- [x] 3.3 Create `frontend/src/shared/types/auth.ts` — shared auth-related types (`User`, `UserPermissions`, `AuthState`)

## 4. AuthContext (Session Management)

- [x] 4.1 Create `frontend/src/features/auth/hooks/useAuth.ts` — `AuthContext` definition and `AuthProvider` component
- [x] 4.2 Implement token storage: access + refresh tokens in memory (context state) and localStorage for hard refresh recovery
- [x] 4.3 Implement `login(email, password)` — calls `POST /api/auth/login`, stores tokens, fetches user via `GET /api/auth/me`, handles 2FA_REQUIRED response
- [x] 4.4 Implement `logout()` — calls `POST /api/auth/logout` (fire-and-forget), clears tokens and user state, redirects to `/login`
- [x] 4.5 Implement boot session restoration: check localStorage for refresh token, call `GET /api/auth/me`, populate user on success or clear on failure
- [x] 4.6 Export `useAuth()` hook with `{ user, isAuthenticated, isLoading, login, logout, getAccessToken, requires2fa }`

## 5. Auth Pages

- [x] 5.1 Create `LoginPage` at `frontend/src/features/auth/pages/LoginPage.tsx` — email + password form with React Hook Form + Zod, submit calls `useAuth().login()`, loading state on submit, backend error display, link to forgot password, redirect to `?redirect=` param on success
- [x] 5.2 Create `TwoFactorPage` at `frontend/src/features/auth/pages/TwoFactorPage.tsx` — 6-digit TOTP input with validation, calls 2FA verify endpoint, completes authentication flow
- [x] 5.3 Create `ForgotPasswordPage` at `frontend/src/features/auth/pages/ForgotPasswordPage.tsx` — email input, calls `POST /api/auth/forgot`, shows success message (same for found/not-found to prevent enumeration)
- [x] 5.4 Create `ResetPasswordPage` at `frontend/src/features/auth/pages/ResetPasswordPage.tsx` — new password + confirm with Zod validation (match check), reads token from query params, calls `POST /api/auth/reset`, redirects to login on success

## 6. Shell (Layout, Route Guard, Router)

- [x] 6.1 Create `ProtectedRoute` at `frontend/src/features/shell/components/ProtectedRoute.tsx` — checks `isAuthenticated`, redirects to `/login?redirect=<current>`, shows spinner while `isLoading`, renders fallback when `requiredPermissions` are missing
- [x] 6.2 Create `Layout` at `frontend/src/features/shell/components/Layout.tsx` — sidebar with collapsible toggle, user info (name), logout button, `<Outlet/>` for page content
- [x] 6.3 Implement sidebar menu items as a data structure (`{ label, path, icon, requiredPermission? }[]`) rendered dynamically based on `user.permissions`
- [x] 6.4 Implement active route highlighting in sidebar based on current location
- [x] 6.5 Create router configuration in `frontend/src/pages/Router.tsx` — public routes (login, 2fa, forgot, reset), protected routes wrapped in Layout, 404 fallback, redirect /login to home if authenticated, redirect unknown routes for unauthenticated users

## 7. Tests

- [x] 7.1 Write test: LoginPage renders email, password fields and submit button
- [x] 7.2 Write test: LoginPage validates empty fields and invalid email (no API call)
- [x] 7.3 Write test: LoginPage calls POST /api/auth/login on valid submit (mocked)
- [x] 7.4 Write test: LoginPage shows backend error message
- [x] 7.5 Write test: LoginPage redirects on successful login
- [x] 7.6 Write test: LoginPage shows loading state during submission
- [x] 7.7 Write test: ProtectedRoute redirects to /login when not authenticated
- [x] 7.8 Write test: ProtectedRoute allows access when authenticated
- [x] 7.9 Write test: ProtectedRoute shows "not authorized" when missing permissions
- [x] 7.10 Write test: AuthContext login/logout flow with mocked API
- [x] 7.11 Write test: HTTP client transparent refresh on 401 (mock two calls, assert retry succeeds)
- [x] 7.12 Write test: HTTP client redirects on failed refresh
- [x] 7.13 Write test: TwoFactorPage validates 6-digit code
- [x] 7.14 Write test: ForgotPasswordPage shows success message after submit
- [x] 7.15 Write test: ResetPasswordPage validates password match

## 8. Final Verification

- [x] 8.1 Run full Vitest test suite — all C-21 tests pass
- [x] 8.2 Run TypeScript type check (`npx tsc --noEmit`)
- [x] 8.3 Run `npm run build` — Vite production build succeeds
- [x] 8.4 Verify dev server starts and renders login page
