## ADDED Requirements

### Requirement: ProtectedRoute guard
The system SHALL provide a `ProtectedRoute` component that guards routes from unauthenticated access and optionally enforces permissions.

#### Scenario: ProtectedRoute redirects unauthenticated users
- **WHEN** an unauthenticated user tries to access a protected route
- **THEN** they SHALL be redirected to `/login`
- **THEN** the original URL SHALL be preserved as a `?redirect=` query parameter

#### Scenario: ProtectedRoute allows authenticated users
- **WHEN** an authenticated user accesses a protected route
- **THEN** the route content SHALL render normally

#### Scenario: ProtectedRoute blocks missing permissions
- **WHEN** an authenticated user without required permissions accesses a protected route
- **THEN** a "not authorized" fallback SHALL be rendered (not a redirect)

#### Scenario: ProtectedRoute shows loading spinner while session loads
- **WHEN** the app is booting and `AuthContext.isLoading` is `true`
- **THEN** a loading spinner SHALL be rendered instead of redirecting to login
- **THEN** once loading resolves, the guard SHALL evaluate normally (redirect or render)

### Requirement: Layout with permission-aware sidebar
The system SHALL provide a `Layout` component with a sidebar menu that adapts to the current user's permissions.

#### Scenario: Layout renders sidebar with menu items
- **WHEN** an authenticated user views the layout
- **THEN** a sidebar with navigation menu items SHALL be rendered
- **THEN** the sidebar SHALL include the user's name and a logout button

#### Scenario: Menu items respect permissions
- **WHEN** a menu item declares `requiredPermission` and the user lacks it
- **THEN** that menu item SHALL be hidden

#### Scenario: Layout highlights active route
- **WHEN** the current URL matches a menu item's path
- **THEN** that menu item SHALL be visually highlighted as active

#### Scenario: Layout is collapsible
- **WHEN** the user clicks the collapse toggle
- **THEN** the sidebar SHALL collapse to icon-only mode (or completely)
- **THEN** collapsed state SHALL persist across navigation

### Requirement: Router structure
The system SHALL define all application routes in a centralized router configuration.

#### Scenario: Public routes are accessible without authentication
- **WHEN** an unauthenticated user navigates to `/login`, `/login/2fa`, `/forgot-password`, or `/reset-password`
- **THEN** the corresponding page SHALL render without redirection

#### Scenario: Authenticated users visiting /login redirect to home
- **WHEN** an authenticated user navigates to `/login`
- **THEN** they SHALL be redirected to `/` (the app home)

#### Scenario: Unknown routes redirect to login or show 404
- **WHEN** an unauthenticated user navigates to an unknown route
- **THEN** they SHALL be redirected to `/login`
- **WHEN** an authenticated user navigates to an unknown route
- **THEN** a 404 page SHALL be rendered within the layout
