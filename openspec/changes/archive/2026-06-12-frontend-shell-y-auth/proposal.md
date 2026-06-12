## Why

This is the first frontend change in the project. All backend foundation (C-01 to C-20) is complete and archived, covering tenancy, auth/JWT/2FA, RBAC, core models, and business logic. The system now needs a web client to consume those APIs. This change scaffolds the SPA shell, auth screens, and the centralized HTTP client — the minimum viable frontend to authenticate, navigate, and display a permission-aware layout.

## What Changes

- New `frontend/` directory at project root with React 18 + TypeScript + Vite
- Feature-based folder structure: `frontend/src/{features/auth,features/shell,shared/{components,hooks,services,types,pages}}`
- Centralized Axios HTTP client with JWT attachment and transparent 401 → refresh → retry
- AuthContext providing login, logout, refresh, and current user with roles/permissions
- Login, 2FA, Forgot Password, Reset Password screens consuming C-03 endpoints
- ProtectedRoute component that checks auth and required permissions
- Layout with sidebar/menu adapting to session permissions
- TanStack Query hooks for data fetching
- React Hook Form + Zod validation schemas for login and recovery forms
- Vitest + React Testing Library test suite
- Logout: client-side session clear + POST /api/auth/logout

## Capabilities

### New Capabilities
- `http-client`: Centralized Axios instance with request interceptor (JWT Bearer token) and response interceptor (catch 401, attempt transparent refresh via `/api/auth/refresh`, retry original request, redirect to login if refresh fails)
- `user-session`: AuthContext that holds current user (id, email, roles, permissions, tenant_id), exposes login/logout/isAuthenticated/isRefreshing, persists tokens
- `auth`: Authentication screens — LoginPage, TwoFactorPage, ForgotPasswordPage, ResetPasswordPage — with React Hook Form + Zod validation, consuming C-03 endpoints
- `shell`: Application shell — Layout with sidebar/menu driven by session permissions, ProtectedRoute guard that blocks unauthenticated users and enforces required permissions

### Modified Capabilities
<!-- No existing capabilities are modified — this is the first frontend change -->

## Impact

- **New directory**: `frontend/` with full React 18 + TypeScript + Vite scaffold
- **New files**: `frontend/src/features/auth/{pages,components,hooks,services,types}`, `frontend/src/features/shell/{components,hooks,types}`, `frontend/src/shared/{components,hooks,services,types,pages}`
- **New dependencies**: `react@18`, `typescript`, `vite`, `tailwindcss`, `@tanstack/react-query`, `react-hook-form`, `zod`, `@hookform/resolvers`, `axios`, `vitest`, `@testing-library/react`, `@testing-library/jest-dom`, `@testing-library/user-event`, `jsdom`
- **No backend changes**: Frontend consumes existing C-03 endpoints (login, refresh, logout, forgot, reset, 2fa/enroll, 2fa/verify, me)
- **Tests**: `frontend/src/features/auth/__tests__/` (login render, auth flow mock, guard redirect without session, transparent refresh)
