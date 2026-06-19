import { useState } from 'react'
import { useMisEquipos, useExportarEquipo } from '../hooks/useEquiposApi'
import type { EquiposFilters, MiEquipo } from '../types'

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
    return <div className="py-8 text-center text-gray-500">Cargando equipos...</div>
  }

  if (isError) {
    return <div className="py-8 text-center text-red-600">Error al cargar equipos.</div>
  }

  const equipos = data?.data ?? []

  return (
    <div>
      <div className="mb-4 flex gap-3">
        <input
          type="text"
          placeholder="Materia ID"
          className="rounded-md border border-gray-300 px-3 py-2 text-sm"
          onChange={(e) => handleFilter('materia_id', e.target.value)}
        />
        <input
          type="text"
          placeholder="Rol"
          className="rounded-md border border-gray-300 px-3 py-2 text-sm"
          onChange={(e) => handleFilter('rol', e.target.value)}
        />
        <select
          className="rounded-md border border-gray-300 px-3 py-2 text-sm"
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
        <div className="rounded-lg bg-gray-50 py-12 text-center text-gray-500">
          Sin equipos asignados para los filtros seleccionados.
        </div>
      ) : (
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                {['Materia', 'Carrera', 'Cohorte', 'Rol', 'Vigencia', 'Estado', 'Acciones'].map(
                  (h) => (
                    <th
                      key={h}
                      className="px-4 py-3 text-left text-xs font-semibold uppercase tracking-wider text-gray-500"
                    >
                      {h}
                    </th>
                  ),
                )}
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-100 bg-white">
              {equipos.map((eq) => (
                <tr key={eq.id} className="hover:bg-gray-50">
                  <td className="px-4 py-3 text-sm text-gray-900">{eq.materia_nombre}</td>
                  <td className="px-4 py-3 text-sm text-gray-600">{eq.carrera}</td>
                  <td className="px-4 py-3 text-sm text-gray-600">{eq.cohorte}</td>
                  <td className="px-4 py-3 text-sm text-gray-600">{eq.rol}</td>
                  <td className="px-4 py-3 text-sm text-gray-600">
                    {eq.vigencia_desde} → {eq.vigencia_hasta}
                  </td>
                  <td className="px-4 py-3">
                    <span
                      className={`inline-flex rounded-full px-2 py-0.5 text-xs font-medium ${
                        eq.activo ? 'bg-green-100 text-green-700' : 'bg-gray-100 text-gray-600'
                      }`}
                    >
                      {eq.activo ? 'Activo' : 'Inactivo'}
                    </span>
                  </td>
                  <td className="px-4 py-3">
                    <div className="flex gap-2">
                      <button
                        type="button"
                        onClick={() => onVigencia(eq)}
                        className="text-xs text-blue-600 hover:underline"
                      >
                        Vigencia
                      </button>
                      <button
                        type="button"
                        onClick={() => exportar.mutate(eq.id)}
                        disabled={exportar.isPending}
                        className="text-xs text-gray-600 hover:underline disabled:opacity-50"
                      >
                        Exportar
                      </button>
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
