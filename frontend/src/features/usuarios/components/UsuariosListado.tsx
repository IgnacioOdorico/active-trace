import { useState } from 'react'
import { useUsuarios, useToggleUsuarioEstado } from '../hooks/useUsuariosApi'
import type { UsuariosFilters, Usuario } from '../types'

interface Props {
  puedeGestionar: boolean
  onEditar: (usuario: Usuario) => void
}

export default function UsuariosListado({ puedeGestionar, onEditar }: Props) {
  const [filters, setFilters] = useState<UsuariosFilters>({ page: 1, page_size: 20 })
  const { data, isLoading } = useUsuarios(filters)
  const { mutate: toggle } = useToggleUsuarioEstado()

  return (
    <div className="space-y-4">
      <div className="flex flex-wrap gap-3 rounded-lg bg-white p-4 shadow-sm">
        <div className="flex flex-col gap-1">
          <label className="text-xs font-medium text-gray-600">Estado</label>
          <select
            className="rounded-md border border-gray-300 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none"
            value={filters.estado ?? ''}
            onChange={(e) => setFilters((f) => ({ ...f, estado: e.target.value || undefined, page: 1 }))}
          >
            <option value="">Todos</option>
            <option value="Activo">Activo</option>
            <option value="Inactivo">Inactivo</option>
          </select>
        </div>
      </div>

      {isLoading && (
        <div className="space-y-2">
          {Array.from({ length: 5 }).map((_, i) => (
            <div key={i} className="h-10 animate-pulse rounded bg-gray-200" />
          ))}
        </div>
      )}

      {!isLoading && data?.data.length === 0 && (
        <p className="py-6 text-center text-sm text-gray-500">
          No hay usuarios para los filtros seleccionados.
        </p>
      )}

      {!isLoading && data && data.data.length > 0 && (
        <>
          <table className="w-full overflow-hidden rounded-lg border border-gray-200 bg-white">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-4 py-2 text-left text-xs font-medium text-gray-500">Nombre</th>
                <th className="px-4 py-2 text-left text-xs font-medium text-gray-500">Email</th>
                <th className="px-4 py-2 text-left text-xs font-medium text-gray-500">Regional</th>
                <th className="px-4 py-2 text-center text-xs font-medium text-gray-500">Modalidad</th>
                <th className="px-4 py-2 text-center text-xs font-medium text-gray-500">Estado</th>
                {puedeGestionar && (
                  <th className="px-4 py-2 text-center text-xs font-medium text-gray-500">Acciones</th>
                )}
              </tr>
            </thead>
            <tbody>
              {data.data.map((u) => (
                <tr key={u.id} className="border-b border-gray-100 hover:bg-gray-50">
                  <td className="px-4 py-2 text-sm font-medium text-gray-900">
                    {u.nombre} {u.apellidos}
                  </td>
                  <td className="px-4 py-2 text-sm text-gray-600">{u.email}</td>
                  <td className="px-4 py-2 text-sm text-gray-600">{u.regional ?? '—'}</td>
                  <td className="px-4 py-2 text-center">
                    <span className={`inline-block rounded-full px-2 py-0.5 text-xs font-medium ${u.facturador ? 'bg-yellow-100 text-yellow-700' : 'bg-blue-100 text-blue-700'}`}>
                      {u.facturador ? 'Factura' : 'Liquidación'}
                    </span>
                  </td>
                  <td className="px-4 py-2 text-center">
                    <span className={`inline-block rounded-full px-2 py-0.5 text-xs font-medium ${u.is_active ? 'bg-green-100 text-green-700' : 'bg-gray-100 text-gray-500'}`}>
                      {u.estado}
                    </span>
                  </td>
                  {puedeGestionar && (
                    <td className="px-4 py-2 text-center">
                      <div className="flex justify-center gap-2">
                        <button onClick={() => onEditar(u)} className="rounded px-2 py-1 text-xs text-blue-600 hover:bg-blue-50">
                          Editar
                        </button>
                        <button
                          onClick={() => toggle({ id: u.id, activo: !u.is_active })}
                          className="rounded px-2 py-1 text-xs text-gray-600 hover:bg-gray-100"
                        >
                          {u.is_active ? 'Desactivar' : 'Activar'}
                        </button>
                      </div>
                    </td>
                  )}
                </tr>
              ))}
            </tbody>
          </table>
          <div className="flex items-center justify-between text-sm text-gray-500">
            <span>Total: {data.total} usuarios</span>
          </div>
        </>
      )}
    </div>
  )
}
