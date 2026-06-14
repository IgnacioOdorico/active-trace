import { Routes, Route, Navigate } from 'react-router-dom'
import { useAuth } from '../features/auth/hooks/useAuth'
import LoginPage from '../features/auth/pages/LoginPage'
import TwoFactorPage from '../features/auth/pages/TwoFactorPage'
import ForgotPasswordPage from '../features/auth/pages/ForgotPasswordPage'
import ResetPasswordPage from '../features/auth/pages/ResetPasswordPage'
import ProtectedRoute from '../features/shell/components/ProtectedRoute'
import Layout from '../features/shell/components/Layout'
import Home from './Home'
import NotFound from './NotFound'
import CalificacionesImportarPage from '../features/calificaciones-importar/pages/CalificacionesImportarPage'
import UmbralPage from '../features/gestion-umbral/pages/UmbralPage'
import AlumnosAtrasadosPage from '../features/alumnos-atrasados/pages/AlumnosAtrasadosPage'
import ReportesPage from '../features/notas-finales-reportes/pages/ReportesPage'
import ComunicacionesPage from '../features/comunicacion-atrasados/pages/ComunicacionesPage'
import MonitoresPage from '../features/monitor-seguimiento/pages/MonitoresPage'

function PublicRoute({ children }: { children: React.ReactNode }) {
  const { isAuthenticated, isLoading } = useAuth()

  if (isLoading) {
    return (
      <div className="flex min-h-screen items-center justify-center">
        <div className="h-8 w-8 animate-spin rounded-full border-4 border-blue-600 border-t-transparent" />
      </div>
    )
  }

  if (isAuthenticated) {
    return <Navigate to="/" replace />
  }

  return <>{children}</>
}

export default function AppRouter() {
  return (
    <Routes>
      <Route
        path="/login"
        element={
          <PublicRoute>
            <LoginPage />
          </PublicRoute>
        }
      />
      <Route
        path="/login/2fa"
        element={
          <PublicRoute>
            <TwoFactorPage />
          </PublicRoute>
        }
      />
      <Route
        path="/forgot-password"
        element={
          <PublicRoute>
            <ForgotPasswordPage />
          </PublicRoute>
        }
      />
      <Route
        path="/reset-password"
        element={
          <PublicRoute>
            <ResetPasswordPage />
          </PublicRoute>
        }
      />
      <Route
        path="/"
        element={
          <ProtectedRoute>
            <Layout />
          </ProtectedRoute>
        }
      >
        <Route index element={<Home />} />
        <Route path="calificaciones/importar" element={<CalificacionesImportarPage />} />
        <Route path="calificaciones/umbral" element={<UmbralPage />} />
        <Route path="alumnos/atrasados" element={<AlumnosAtrasadosPage />} />
        <Route path="reportes" element={<ReportesPage />} />
        <Route path="comunicaciones" element={<ComunicacionesPage />} />
        <Route path="monitores" element={<MonitoresPage />} />
        <Route path="*" element={<NotFound />} />
      </Route>
    </Routes>
  )
}
