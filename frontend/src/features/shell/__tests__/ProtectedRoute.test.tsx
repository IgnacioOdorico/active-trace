import { render, screen } from '@testing-library/react'
import { MemoryRouter, Routes, Route } from 'react-router-dom'
import { describe, it, expect, vi } from 'vitest'
import ProtectedRoute from '../components/ProtectedRoute'

const mockUseAuth = vi.fn()

vi.mock('../../auth/hooks/useAuth', () => ({
  useAuth: () => mockUseAuth(),
}))

function renderWithRouter(
  initialEntries: string[],
  path: string,
  children: React.ReactNode,
) {
  return render(
    <MemoryRouter initialEntries={initialEntries}>
      <Routes>
        <Route path="/login" element={<div>Login Page</div>} />
        <Route
          path={path}
          element={<ProtectedRoute>{children}</ProtectedRoute>}
        />
      </Routes>
    </MemoryRouter>,
  )
}

describe('ProtectedRoute', () => {
  it('redirects to /login when not authenticated', () => {
    mockUseAuth.mockReturnValue({
      isAuthenticated: false,
      isLoading: false,
      user: null,
    })

    renderWithRouter(['/protected'], '/protected', <div>Protected Content</div>)

    expect(screen.getByText('Login Page')).toBeInTheDocument()
    expect(screen.queryByText('Protected Content')).not.toBeInTheDocument()
  })

  it('allows access when authenticated', () => {
    mockUseAuth.mockReturnValue({
      isAuthenticated: true,
      isLoading: false,
      user: { permissions: [] },
    })

    renderWithRouter(['/protected'], '/protected', <div>Protected Content</div>)

    expect(screen.getByText('Protected Content')).toBeInTheDocument()
  })

  it('shows not authorized when missing permissions', () => {
    mockUseAuth.mockReturnValue({
      isAuthenticated: true,
      isLoading: false,
      user: { permissions: ['basic.access'] },
    })

    render(
      <MemoryRouter initialEntries={['/permission-test']}>
        <Routes>
          <Route path="/login" element={<div>Login Page</div>} />
          <Route
            path="/permission-test"
            element={
              <ProtectedRoute requiredPermissions={['admin.access']}>
                <div>Protected Content</div>
              </ProtectedRoute>
            }
          />
        </Routes>
      </MemoryRouter>,
    )

    expect(screen.getByText('Acceso Denegado')).toBeInTheDocument()
    expect(screen.queryByText('Protected Content')).not.toBeInTheDocument()
  })
})
