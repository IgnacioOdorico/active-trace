import { useMemo, useState } from 'react'
import { useGuardias, useExportarGuardias } from '../hooks/useEncuentrosAdminApi'
import { useMaterias } from '../../academico/hooks/useMaterias'
import { useCarreras } from '../../estructura-academica/hooks/useEstructuraApi'
import type { GuardiasFilters, GuardiaEstado } from '../types'

const ESTADO_COLORS: Record<GuardiaEstado, string> = {
  Pendiente: 'bg-yellow-100 text-yellow-700',
  Realizada: 'bg-green-100 text-green-700',
  Cancelada: 'bg-red-100 text-red-700',
}

export default function GestionGuardias() {
  const [filters, setFilters] = useState<GuardiasFilters>({})
  const { data, isLoading, isError } = useGuardias(filters)
  const exportar = useExportarGuardias()
  const { data: materias } = useMaterias()
  const { data: carreras } = useCarreras()

  const nombreMateria = useMemo(() => {
    const mapa = new Map(materias?.map((m) => [m.id, m.nombre]))
    return (materiaId: string) => mapa.get(materiaId) ?? materiaId
  }, [materias])

  const nombreCarrera = useMemo(() => {
    const mapa = new Map(carreras?.map((c) => [c.id, c.nombre]))
    return (carreraId: string) => mapa.get(carreraId) ?? carreraId
  }, [carreras])

  const handleFilter = (key: keyof GuardiasFilters, value: string) => {
    setFilters((prev) => ({ ...prev, [key]: value || undefined }))
  }

  if (isLoading) return <div className="py-8 text-center text-gray-500">Cargando guardias...</div>
  if (isError) return <div className="py-8 text-center text-red-600">Error al cargar guardias.</div>

  const guardias = data?.items ?? []

  return (
    <div>
      <div className="mb-4 flex flex-wrap items-center gap-3">
        <input
          type="text"
          placeholder="Materia ID"
          className="rounded-md border border-gray-300 px-3 py-2 text-sm"
          onChange={(e) => handleFilter('materia_id', e.target.value)}
        />
        <input
          type="text"
          placeholder="Asignación ID"
          className="rounded-md border border-gray-300 px-3 py-2 text-sm"
          onChange={(e) => handleFilter('asignacion_id', e.target.value)}
        />
        <button
          type="button"
          onClick={() => exportar.mutate()}
          disabled={exportar.isPending}
          className="ml-auto rounded-md bg-gray-100 px-3 py-2 text-sm font-medium text-gray-700 hover:bg-gray-200 disabled:opacity-50"
        >
          {exportar.isPending ? 'Exportando...' : 'Exportar'}
        </button>
      </div>

      {guardias.length === 0 ? (
        <div className="rounded-lg bg-gray-50 py-12 text-center text-gray-500">
          No hay guardias para los filtros seleccionados.
        </div>
      ) : (
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                {['Materia', 'Carrera', 'Día', 'Horario', 'Estado', 'Comentarios'].map((h) => (
                  <th
                    key={h}
                    className="px-4 py-3 text-left text-xs font-semibold uppercase tracking-wider text-gray-500"
                  >
                    {h}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-100 bg-white">
              {guardias.map((g) => (
                <tr key={g.id} className="hover:bg-gray-50">
                  <td className="px-4 py-3 text-sm text-gray-900">{nombreMateria(g.materia_id)}</td>
                  <td className="px-4 py-3 text-sm text-gray-600">{nombreCarrera(g.carrera_id)}</td>
                  <td className="px-4 py-3 text-sm text-gray-600">{g.dia}</td>
                  <td className="px-4 py-3 text-sm text-gray-600">{g.horario}</td>
                  <td className="px-4 py-3">
                    <span
                      className={`inline-flex rounded-full px-2 py-0.5 text-xs font-medium ${ESTADO_COLORS[g.estado]}`}
                    >
                      {g.estado}
                    </span>
                  </td>
                  <td className="px-4 py-3 text-sm text-gray-500">{g.comentarios ?? '—'}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  )
}
