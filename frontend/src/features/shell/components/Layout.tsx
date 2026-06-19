import { Outlet, NavLink } from 'react-router-dom'
import { useAuth } from '../../auth/hooks/useAuth'
import { hasPermission } from '../../../shared/utils/permissions'

interface MenuItem {
  label: string
  path: string
  icon: string
  requiredPermission?: string
}

interface MenuSection {
  label: string
  items: MenuItem[]
}

const menuSections: MenuSection[] = [
  {
    label: 'General',
    items: [
      { label: 'Inicio', path: '/', icon: 'home' },
      { label: 'Avisos', path: '/coordinacion/avisos', icon: 'campaign' },
    ],
  },
  {
    label: 'Académico',
    items: [
      {
        label: 'Importar Calificaciones',
        path: '/calificaciones/importar',
        icon: 'upload_file',
        requiredPermission: 'calificaciones:importar',
      },
      {
        label: 'Umbral de Aprobación',
        path: '/calificaciones/umbral',
        icon: 'tune',
        requiredPermission: 'calificaciones:importar',
      },
      {
        label: 'Alumnos Atrasados',
        path: '/alumnos/atrasados',
        icon: 'warning',
        requiredPermission: 'atrasados:ver',
      },
      {
        label: 'Reportes y Notas',
        path: '/reportes',
        icon: 'analytics',
        requiredPermission: 'reportes:ver',
      },
      {
        label: 'Comunicaciones',
        path: '/comunicaciones',
        icon: 'mail',
        requiredPermission: 'comunicaciones:enviar',
      },
      {
        label: 'Monitores',
        path: '/monitores',
        icon: 'supervised_user_circle',
        requiredPermission: 'monitores:ver',
      },
    ],
  },
  {
    label: 'Coordinación',
    items: [
      {
        label: 'Equipos Docentes',
        path: '/coordinacion/equipos',
        icon: 'groups',
        requiredPermission: 'equipos:asignar',
      },
      {
        label: 'Tareas',
        path: '/coordinacion/tareas',
        icon: 'task',
        requiredPermission: 'tareas:gestionar(propio)',
      },
      {
        label: 'Encuentros (Admin)',
        path: '/coordinacion/encuentros',
        icon: 'event',
        requiredPermission: 'encuentros:gestionar',
      },
      {
        label: 'Coloquios',
        path: '/coordinacion/coloquios',
        icon: 'forum',
        requiredPermission: 'equipos:asignar',
      },
      {
        label: 'Setup Cuatrimestre',
        path: '/coordinacion/setup',
        icon: 'settings_applications',
        requiredPermission: 'equipos:asignar',
      },
      {
        label: 'Monitores Coord.',
        path: '/coordinacion/monitores',
        icon: 'admin_panel_settings',
        requiredPermission: 'monitores:ver',
      },
    ],
  },
  {
    label: 'Finanzas',
    items: [
      {
        label: 'Liquidaciones',
        path: '/finanzas/liquidaciones',
        icon: 'payments',
        requiredPermission: 'liquidaciones:ver',
      },
      {
        label: 'Grilla Salarial',
        path: '/finanzas/grilla-salarial',
        icon: 'request_quote',
        requiredPermission: 'liquidaciones:configurar-salarios',
      },
      {
        label: 'Facturas',
        path: '/finanzas/facturas',
        icon: 'receipt',
        requiredPermission: 'facturas:ver',
      },
    ],
  },
  {
    label: 'Administración',
    items: [
      {
        label: 'Estructura Académica',
        path: '/admin/estructura',
        icon: 'account_balance',
        requiredPermission: 'estructura:gestionar',
      },
      {
        label: 'Usuarios',
        path: '/admin/usuarios',
        icon: 'manage_accounts',
        requiredPermission: 'usuarios:gestionar',
      },
      {
        label: 'Panel de Auditoría',
        path: '/admin/auditoria',
        icon: 'history',
        requiredPermission: 'auditoria:ver',
      },
    ],
  },
]

export default function Layout() {
  const { user, logout } = useAuth()

  return (
    <div className="flex h-screen bg-background overflow-hidden">
      {/* SideNavBar */}
      <aside className="w-64 bg-surface-container-low border-r border-outline-variant flex flex-col flex-shrink-0">
        <div className="h-16 flex items-center px-6 border-b border-outline-variant">
          <span className="material-symbols-outlined text-primary mr-2">account_balance</span>
          <h1 className="font-headline-sm text-headline-sm text-primary">Active Trace</h1>
        </div>

        <nav className="flex-1 overflow-y-auto py-4">
          {menuSections.map((section) => {
            const visibleItems = section.items.filter((item) => {
              if (!item.requiredPermission) return true
              const perms = user?.permissions ?? []
              return hasPermission(perms, item.requiredPermission)
            })

            if (visibleItems.length === 0) return null

            return (
              <div key={section.label} className="mb-6">
                <p className="px-6 mb-2 font-label-caps text-label-caps text-outline uppercase">
                  {section.label}
                </p>
                <ul className="space-y-1">
                  {visibleItems.map((item) => (
                    <li key={item.path}>
                      <NavLink
                        to={item.path}
                        end
                        className={({ isActive }) =>
                          `relative flex items-center px-6 py-2 font-body-md text-body-md transition-colors ${
                            isActive
                              ? 'text-primary bg-surface-container-high font-medium'
                              : 'text-on-surface-variant hover:bg-surface-container hover:text-on-surface'
                          }`
                        }
                      >
                        {({ isActive }) => (
                          <>
                            {isActive && <div className="active-tab-indicator" />}
                            <span className="material-symbols-outlined mr-3 text-[20px]">
                              {item.icon}
                            </span>
                            {item.label}
                          </>
                        )}
                      </NavLink>
                    </li>
                  ))}
                </ul>
              </div>
            )
          })}
        </nav>
      </aside>

      {/* Main Content Area */}
      <div className="flex-1 flex flex-col min-w-0">
        {/* TopNavBar */}
        <header className="h-16 bg-surface border-b border-outline-variant flex items-center justify-between px-8 flex-shrink-0">
          <div className="flex items-center gap-4">
            <h2 className="font-headline-sm text-headline-sm text-on-surface">
              Área de Trabajo
            </h2>
          </div>
          
          <div className="flex items-center gap-6">
            <div className="flex items-center gap-3">
              <div className="text-right">
                <p className="font-body-md text-body-md text-on-surface font-medium leading-tight">
                  {user?.nombre || 'Usuario'}
                </p>
                <p className="font-label-caps text-[10px] text-outline uppercase tracking-wider">
                  {user?.roles?.[0] || 'Rol'}
                </p>
              </div>
              <div className="w-8 h-8 rounded-full bg-primary-container text-on-primary-container flex items-center justify-center font-label-caps font-bold">
                {user?.nombre?.charAt(0).toUpperCase() || 'U'}
              </div>
            </div>
            <div className="h-6 w-px bg-outline-variant"></div>
            <button
              onClick={logout}
              className="flex items-center gap-2 text-error hover:text-opacity-80 transition-colors font-label-caps text-label-caps uppercase"
              title="Cerrar sesión"
            >
              <span className="material-symbols-outlined text-[20px]">logout</span>
              Salir
            </button>
          </div>
        </header>

        {/* Workspace */}
        <main className="flex-1 overflow-auto p-8 bg-background">
          <div className="max-w-7xl mx-auto">
            <Outlet />
          </div>
        </main>
      </div>
    </div>
  )
}
