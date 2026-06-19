import { useState } from 'react'
import { useUsuarios, useToggleUsuarioEstado } from '../hooks/useUsuariosApi'
import type { UsuariosFilters, Usuario } from '../types'
import { Badge } from '../../../shared/components/ui/Badge'
import { Button } from '../../../shared/components/ui/Button'

interface Props {
  puedeGestionar: boolean
  onEditar: (usuario: Usuario) => void
}

export default function UsuariosListado({ puedeGestionar, onEditar }: Props) {
  const [filters, setFilters] = useState<UsuariosFilters>({ page: 1, page_size: 20 })
  const { data, isLoading } = useUsuarios(filters)
  const { mutate: toggle } = useToggleUsuarioEstado()

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap gap-4">
        <div className="flex flex-col gap-2">
          <label className="font-label-caps text-label-caps uppercase text-on-surface-variant">Estado</label>
          <select
            className="w-48 neo-latex-border rounded bg-surface-container-lowest px-3 py-2 font-body-md text-on-surface focus:border-primary focus:outline-none focus:ring-1 focus:ring-primary"
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
            <div key={i} className="h-10 animate-pulse rounded bg-surface-container" />
          ))}
        </div>
      )}

      {!isLoading && data?.data.length === 0 && (
        <div className="rounded neo-latex-border bg-surface-container py-12 text-center font-body-md text-on-surface-variant">
          No hay usuarios para los filtros seleccionados.
        </div>
      )}

      {!isLoading && data && data.data.length > 0 && (
        <>
          <div className="overflow-x-auto rounded neo-latex-border bg-surface-container-lowest">
            <table className="min-w-full divide-y divide-outline-variant">
              <thead className="bg-surface">
                <tr>
                  <th className="px-4 py-3 text-left font-label-caps text-label-caps uppercase text-on-surface-variant">Nombre</th>
                  <th className="px-4 py-3 text-left font-label-caps text-label-caps uppercase text-on-surface-variant">Email</th>
                  <th className="px-4 py-3 text-left font-label-caps text-label-caps uppercase text-on-surface-variant">Regional</th>
                  <th className="px-4 py-3 text-center font-label-caps text-label-caps uppercase text-on-surface-variant">Modalidad</th>
                  <th className="px-4 py-3 text-center font-label-caps text-label-caps uppercase text-on-surface-variant">Estado</th>
                  {puedeGestionar && (
                    <th className="px-4 py-3 text-center font-label-caps text-label-caps uppercase text-on-surface-variant">Acciones</th>
                  )}
                </tr>
              </thead>
              <tbody className="divide-y divide-outline-variant bg-surface-container-lowest">
                {data.data.map((u) => (
                  <tr key={u.id} className="hover:bg-surface-container transition-colors">
                    <td className="px-4 py-3 font-body-md text-body-md font-medium text-on-surface">
                      {u.nombre} {u.apellidos}
                    </td>
                    <td className="px-4 py-3 font-body-md text-body-md text-on-surface-variant">{u.email}</td>
                    <td className="px-4 py-3 font-body-md text-body-md text-on-surface-variant">{u.regional ?? '—'}</td>
                    <td className="px-4 py-3 text-center">
                      <Badge variant={u.facturador ? 'warning' : 'info'}>
                        {u.facturador ? 'Factura' : 'Liquidación'}
                      </Badge>
                    </td>
                    <td className="px-4 py-3 text-center">
                      <Badge variant={u.is_active ? 'success' : 'neutral'}>
                        {u.estado}
                      </Badge>
                    </td>
                    {puedeGestionar && (
                      <td className="px-4 py-3 text-center">
                        <div className="flex justify-center gap-2">
                          <Button 
                            onClick={() => onEditar(u)} 
                            variant="ghost" 
                            size="sm"
                          >
                            Editar
                          </Button>
                          <Button
                            onClick={() => toggle({ id: u.id, activo: !u.is_active })}
                            variant="ghost"
                            size="sm"
                          >
                            {u.is_active ? 'Desactivar' : 'Activar'}
                          </Button>
                        </div>
                      </td>
                    )}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          <div className="flex items-center justify-between font-body-md text-on-surface-variant">
            <span>Total: {data.total} usuarios</span>
          </div>
        </>
      )}
    </div>
  )
}
