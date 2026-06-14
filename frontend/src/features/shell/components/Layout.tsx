import { useState } from 'react'
import { Outlet, NavLink } from 'react-router-dom'
import { useAuth } from '../../auth/hooks/useAuth'

interface MenuItem {
  label: string
  path: string
  requiredPermission?: string
}

interface MenuSection {
  label: string
  items: MenuItem[]
}

const menuSections: MenuSection[] = [
  {
    label: 'General',
    items: [{ label: 'Inicio', path: '/' }],
  },
  {
    label: 'Académico',
    items: [
      {
        label: 'Importar Calificaciones',
        path: '/calificaciones/importar',
        requiredPermission: 'calificaciones:importar',
      },
      {
        label: 'Umbral de Aprobación',
        path: '/calificaciones/umbral',
        requiredPermission: 'calificaciones:umbral',
      },
      {
        label: 'Alumnos Atrasados',
        path: '/alumnos/atrasados',
        requiredPermission: 'alumnos:atrasados',
      },
      {
        label: 'Reportes y Notas',
        path: '/reportes',
        requiredPermission: 'reportes:ver',
      },
      {
        label: 'Comunicaciones',
        path: '/comunicaciones',
        requiredPermission: 'comunicaciones:enviar',
      },
      {
        label: 'Monitores',
        path: '/monitores',
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
        requiredPermission: 'equipos:asignar',
      },
      {
        label: 'Avisos',
        path: '/coordinacion/avisos',
        requiredPermission: 'avisos:publicar',
      },
      {
        label: 'Tareas',
        path: '/coordinacion/tareas',
        requiredPermission: 'tareas:gestionar',
      },
      {
        label: 'Encuentros (Admin)',
        path: '/coordinacion/encuentros',
        requiredPermission: 'encuentros:gestionar',
      },
      {
        label: 'Coloquios',
        path: '/coordinacion/coloquios',
        requiredPermission: 'equipos:asignar',
      },
      {
        label: 'Setup Cuatrimestre',
        path: '/coordinacion/setup',
        requiredPermission: 'equipos:asignar',
      },
      {
        label: 'Monitores Coord.',
        path: '/coordinacion/monitores',
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
        requiredPermission: 'liquidaciones:ver',
      },
      {
        label: 'Grilla Salarial',
        path: '/finanzas/grilla-salarial',
        requiredPermission: 'liquidaciones:configurar-salarios',
      },
      {
        label: 'Facturas',
        path: '/finanzas/facturas',
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
        requiredPermission: 'estructura:gestionar',
      },
      {
        label: 'Usuarios',
        path: '/admin/usuarios',
        requiredPermission: 'usuarios:gestionar',
      },
      {
        label: 'Panel de Auditoría',
        path: '/admin/auditoria',
        requiredPermission: 'auditoria:ver',
      },
    ],
  },
]

export default function Layout() {
  const { user, logout } = useAuth()
  const [collapsed, setCollapsed] = useState(false)

  return (
    <div className="flex min-h-screen bg-gray-100">
      <aside
        className={`flex flex-col border-r border-gray-200 bg-white transition-all duration-200 ${
          collapsed ? 'w-16' : 'w-64'
        }`}
      >
        <div className="flex items-center justify-between border-b border-gray-200 p-4">
          {!collapsed && (
            <h1 className="text-lg font-bold text-gray-900">Active Trace</h1>
          )}
          <button
            onClick={() => setCollapsed(!collapsed)}
            className="rounded-md p-1 text-gray-500 hover:bg-gray-100 hover:text-gray-700"
            aria-label={collapsed ? 'Expandir menú' : 'Colapsar menú'}
          >
            {collapsed ? '→' : '←'}
          </button>
        </div>

        <nav className="flex-1 space-y-4 overflow-y-auto p-2">
          {menuSections.map((section) => {
            const visibleItems = section.items.filter((item) => {
              if (!item.requiredPermission) return true
              const perms = user?.permissions ?? []
              return perms.includes('*:*') || perms.includes(item.requiredPermission)
            })

            if (visibleItems.length === 0) return null

            return (
              <div key={section.label}>
                {!collapsed && (
                  <p className="px-3 py-1 text-xs font-semibold uppercase tracking-wider text-gray-500">
                    {section.label}
                  </p>
                )}
                <ul className="space-y-1">
                  {visibleItems.map((item) => (
                    <li key={item.path}>
                      <NavLink
                        to={item.path}
                        end
                        className={({ isActive }) =>
                          `flex items-center rounded-md px-3 py-2 text-sm font-medium transition-colors ${
                            isActive
                              ? 'bg-blue-50 text-blue-700'
                              : 'text-gray-700 hover:bg-gray-50 hover:text-gray-900'
                          }`
                        }
                      >
                        {collapsed ? (
                          <span className="mx-auto">
                            {item.label.charAt(0)}
                          </span>
                        ) : (
                          item.label
                        )}
                      </NavLink>
                    </li>
                  ))}
                </ul>
              </div>
            )
          })}
        </nav>

        <div className="border-t border-gray-200 p-4">
          {!collapsed && user && (
            <p className="mb-2 truncate text-sm font-medium text-gray-900">
              {user.nombre}
            </p>
          )}
          <button
            onClick={logout}
            className="w-full rounded-md bg-red-50 px-3 py-2 text-sm font-medium text-red-700 hover:bg-red-100"
          >
            {collapsed ? '×' : 'Cerrar Sesión'}
          </button>
        </div>
      </aside>

      <main className="flex-1 p-6">
        <Outlet />
      </main>
    </div>
  )
}
