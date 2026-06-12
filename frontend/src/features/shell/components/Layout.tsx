import { useState } from 'react'
import { Outlet, NavLink } from 'react-router-dom'
import { useAuth } from '../../auth/hooks/useAuth'

interface MenuItem {
  label: string
  path: string
  requiredPermission?: string
}

const menuItems: MenuItem[] = [
  { label: 'Inicio', path: '/' },
]

export default function Layout() {
  const { user, logout } = useAuth()
  const [collapsed, setCollapsed] = useState(false)

  const visibleItems = menuItems.filter((item) => {
    if (!item.requiredPermission) return true
    return user?.permissions.includes(item.requiredPermission)
  })

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

        <nav className="flex-1 p-2">
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
                    <span className="mx-auto">{item.label.charAt(0)}</span>
                  ) : (
                    item.label
                  )}
                </NavLink>
              </li>
            ))}
          </ul>
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
