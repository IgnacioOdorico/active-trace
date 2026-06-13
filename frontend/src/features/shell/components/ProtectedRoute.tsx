import { Navigate, useLocation } from 'react-router-dom'
import { useAuth } from '../../auth/hooks/useAuth'
import type { ReactNode } from 'react'

interface ProtectedRouteProps {
  children: ReactNode
  requiredPermissions?: string[]
}

export default function ProtectedRoute({
  children,
  requiredPermissions,
}: ProtectedRouteProps) {
  const { isAuthenticated, isLoading, user } = useAuth()
  const location = useLocation()

  if (isLoading) {
    return (
      <div className="flex min-h-screen items-center justify-center">
        <div className="h-8 w-8 animate-spin rounded-full border-4 border-blue-600 border-t-transparent" />
      </div>
    )
  }

  if (!isAuthenticated) {
    const redirectPath = `/login?redirect=${encodeURIComponent(
      location.pathname + location.search,
    )}`
    return <Navigate to={redirectPath} replace />
  }

  if (requiredPermissions && requiredPermissions.length > 0 && user) {
    const hasAllPermissions =
      user.permissions.includes('*:*') ||
      requiredPermissions.every((perm) => user.permissions.includes(perm))
    if (!hasAllPermissions) {
      return (
        <div className="flex min-h-screen items-center justify-center">
          <div className="text-center">
            <h1 className="text-2xl font-bold text-gray-900">
              Acceso Denegado
            </h1>
            <p className="mt-2 text-gray-600">
              No tiene los permisos necesarios para acceder a esta página.
            </p>
          </div>
        </div>
      )
    }
  }

  return <>{children}</>
}
