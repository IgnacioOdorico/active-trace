import { Navigate, useLocation } from 'react-router-dom'
import { useAuth } from '../../auth/hooks/useAuth'
import type { ReactNode } from 'react'
import { BentoCard } from '../../../shared/components/ui/BentoCard'
import { hasAllPermissions } from '../../../shared/utils/permissions'

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
      <div className="flex min-h-screen items-center justify-center bg-surface-container-lowest">
        <div className="h-8 w-8 animate-spin rounded-full border-4 border-primary border-t-transparent" />
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
    if (!hasAllPermissions(user.permissions, requiredPermissions)) {
      return (
        <div className="flex min-h-screen items-center justify-center bg-surface-container-lowest p-4">
          <div className="w-full max-w-md">
            <BentoCard>
              <div className="text-center py-10 px-6">
                <h1 className="font-headline-sm text-headline-sm text-on-surface mb-2">
                  Acceso Denegado
                </h1>
                <p className="font-body-md text-body-md text-on-surface-variant">
                  No tiene los permisos necesarios para acceder a esta página.
                </p>
              </div>
            </BentoCard>
          </div>
        </div>
      )
    }
  }

  return <>{children}</>
}
