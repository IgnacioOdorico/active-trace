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
import EquiposPage from '../features/equipos/pages/EquiposPage'
import AvisosPage from '../features/avisos/pages/AvisosPage'
import TareasPage from '../features/tareas/pages/TareasPage'
import EncuentrosAdminPage from '../features/encuentros-admin/pages/EncuentrosAdminPage'
import ColoquiosPage from '../features/coloquios/pages/ColoquiosPage'
import SetupCuatrimestrePage from '../features/setup-cuatrimestre/pages/SetupCuatrimestrePage'
import MonitoresCoordinacionPage from '../features/monitor-seguimiento/pages/MonitoresCoordinacionPage'
import LiquidacionesPage from '../features/liquidaciones/pages/LiquidacionesPage'
import GrillaSalarialPage from '../features/grilla-salarial/pages/GrillaSalarialPage'
import FacturasPage from '../features/facturas/pages/FacturasPage'
import EstructuraAcademicaPage from '../features/estructura-academica/pages/EstructuraAcademicaPage'
import UsuariosPage from '../features/usuarios/pages/UsuariosPage'
import PanelAuditoriaPage from '../features/panel-auditoria/pages/PanelAuditoriaPage'

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
        {/* Coordinación */}
        <Route path="coordinacion/equipos" element={<EquiposPage />} />
        <Route path="coordinacion/avisos" element={<AvisosPage />} />
        <Route path="coordinacion/tareas" element={<TareasPage />} />
        <Route path="coordinacion/encuentros" element={<EncuentrosAdminPage />} />
        <Route path="coordinacion/coloquios" element={<ColoquiosPage />} />
        <Route path="coordinacion/setup" element={<SetupCuatrimestrePage />} />
        <Route path="coordinacion/monitores" element={<MonitoresCoordinacionPage />} />
        {/* Finanzas */}
        <Route path="finanzas/liquidaciones" element={<LiquidacionesPage />} />
        <Route path="finanzas/grilla-salarial" element={<GrillaSalarialPage />} />
        <Route path="finanzas/facturas" element={<FacturasPage />} />
        {/* Administración */}
        <Route path="admin/estructura" element={<EstructuraAcademicaPage />} />
        <Route path="admin/usuarios" element={<UsuariosPage />} />
        <Route path="admin/auditoria" element={<PanelAuditoriaPage />} />
        <Route path="*" element={<NotFound />} />
      </Route>
    </Routes>
  )
}
