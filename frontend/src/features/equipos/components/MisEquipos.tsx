import { useState } from 'react'
import { useMisEquipos, useExportarEquipo } from '../hooks/useEquiposApi'
import type { EquiposFilters, MiEquipo } from '../types'
import { Badge } from '../../../shared/components/ui/Badge'
import { Button } from '../../../shared/components/ui/Button'

interface MisEquiposProps {
  onVigencia: (equipo: MiEquipo) => void
}

export default function MisEquipos({ onVigencia }: MisEquiposProps) {
  const [filters, setFilters] = useState<EquiposFilters>({})
  const { data, isLoading, isError } = useMisEquipos(filters)
  const exportar = useExportarEquipo()

  const handleFilter = (key: keyof EquiposFilters, value: string) => {
    setFilters((prev) => ({ ...prev, [key]: value || undefined }))
  }

  if (isLoading) {
    return (
      <div className="flex flex-col items-center justify-center py-16">
        <span className="material-symbols-outlined text-primary text-4xl animate-spin">refresh</span>
        <p className="mt-4 font-body-md text-on-surface-variant">Cargando equipos...</p>
      </div>
    )
  }

  if (isError) {
    return <div className="py-8 text-center font-body-md text-error">Error al cargar equipos.</div>
  }

  const equipos = data?.data ?? []

  return (
    <div>
      <div className="mb-6 flex flex-wrap gap-4">
        <input
          type="text"
          placeholder="Materia ID"
          className="w-48 neo-latex-border rounded bg-surface-container-lowest px-3 py-2 font-body-md text-on-surface focus:border-primary focus:outline-none focus:ring-1 focus:ring-primary"
          onChange={(e) => handleFilter('materia_id', e.target.value)}
        />
        <input
          type="text"
          placeholder="Rol"
          className="w-48 neo-latex-border rounded bg-surface-container-lowest px-3 py-2 font-body-md text-on-surface focus:border-primary focus:outline-none focus:ring-1 focus:ring-primary"
          onChange={(e) => handleFilter('rol', e.target.value)}
        />
        <select
          className="w-48 neo-latex-border rounded bg-surface-container-lowest px-3 py-2 font-body-md text-on-surface focus:border-primary focus:outline-none focus:ring-1 focus:ring-primary"
          onChange={(e) => {
            const v = e.target.value
            setFilters((prev) => ({
              ...prev,
              activo: v === '' ? undefined : v === 'true',
            }))
          }}
        >
          <option value="">Todos los estados</option>
          <option value="true">Activo</option>
          <option value="false">Inactivo</option>
        </select>
      </div>

      {equipos.length === 0 ? (
        <div className="rounded neo-latex-border bg-surface-container py-12 text-center font-body-md text-on-surface-variant">
          Sin equipos asignados para los filtros seleccionados.
        </div>
      ) : (
        <div className="overflow-x-auto rounded neo-latex-border bg-surface-container-lowest">
          <table className="min-w-full divide-y divide-outline-variant">
            <thead className="bg-surface">
              <tr>
                {['Materia', 'Carrera', 'Cohorte', 'Rol', 'Vigencia', 'Estado', 'Acciones'].map(
                  (h) => (
                    <th
                      key={h}
                      className="px-4 py-3 text-left font-label-caps text-label-caps uppercase text-on-surface-variant"
                    >
                      {h}
                    </th>
                  ),
                )}
              </tr>
            </thead>
            <tbody className="divide-y divide-outline-variant bg-surface-container-lowest">
              {equipos.map((eq) => (
                <tr key={eq.id} className="hover:bg-surface-container transition-colors">
                  <td className="px-4 py-3 font-body-md text-body-md font-medium text-on-surface">{eq.materia_nombre}</td>
                  <td className="px-4 py-3 font-body-md text-body-md text-on-surface-variant">{eq.carrera}</td>
                  <td className="px-4 py-3 font-body-md text-body-md text-on-surface-variant">{eq.cohorte}</td>
                  <td className="px-4 py-3 font-body-md text-body-md text-on-surface-variant">{eq.rol}</td>
                  <td className="px-4 py-3 font-body-md text-body-md text-on-surface-variant">
                    {eq.vigencia_desde} → {eq.vigencia_hasta}
                  </td>
                  <td className="px-4 py-3">
                    <Badge variant={eq.activo ? 'success' : 'neutral'}>
                      {eq.activo ? 'Activo' : 'Inactivo'}
                    </Badge>
                  </td>
                  <td className="px-4 py-3">
                    <div className="flex gap-2">
                      <Button
                        onClick={() => onVigencia(eq)}
                        variant="ghost"
                        size="sm"
                      >
                        Vigencia
                      </Button>
                      <Button
                        onClick={() => exportar.mutate(eq.id)}
                        disabled={exportar.isPending}
                        variant="ghost"
                        size="sm"
                      >
                        Exportar
                      </Button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  )
}
