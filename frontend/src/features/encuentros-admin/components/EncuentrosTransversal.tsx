import { useState } from 'react'
import { useEncuentrosInstancias } from '../hooks/useEncuentrosAdminApi'
import type { EncuentrosFilters, EncuentroEstado } from '../types'

const ESTADO_COLORS: Record<EncuentroEstado, string> = {
  pendiente: 'bg-yellow-100 text-yellow-700',
  realizado: 'bg-green-100 text-green-700',
  cancelado: 'bg-red-100 text-red-700',
}

export default function EncuentrosTransversal() {
  const [filters, setFilters] = useState<EncuentrosFilters>({})
  const { data, isLoading, isError } = useEncuentrosInstancias(filters)

  const handleFilter = (key: keyof EncuentrosFilters, value: string) => {
    setFilters((prev) => ({ ...prev, [key]: value || undefined }))
  }

  if (isLoading) return <div className="py-8 text-center text-gray-500">Cargando encuentros...</div>
  if (isError) return <div className="py-8 text-center text-red-600">Error al cargar encuentros.</div>

  const encuentros = data?.data ?? []

  return (
    <div>
      <div className="mb-4 flex gap-3">
        <input
          type="text"
          placeholder="Materia ID"
          className="rounded-md border border-gray-300 px-3 py-2 text-sm"
          onChange={(e) => handleFilter('materia_id', e.target.value)}
        />
        <select
          className="rounded-md border border-gray-300 px-3 py-2 text-sm"
          onChange={(e) => handleFilter('estado', e.target.value)}
        >
          <option value="">Todos los estados</option>
          <option value="pendiente">Pendiente</option>
          <option value="realizado">Realizado</option>
          <option value="cancelado">Cancelado</option>
        </select>
      </div>

      {encuentros.length === 0 ? (
        <div className="rounded-lg bg-gray-50 py-12 text-center text-gray-500">
          No hay encuentros para los filtros seleccionados.
        </div>
      ) : (
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                {['Materia', 'Docente', 'Fecha', 'Horario', 'Estado', 'Links'].map((h) => (
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
              {encuentros.map((enc) => (
                <tr key={enc.id} className="hover:bg-gray-50">
                  <td className="px-4 py-3 text-sm text-gray-900">{enc.materia_nombre}</td>
                  <td className="px-4 py-3 text-sm text-gray-600">{enc.docente_nombre}</td>
                  <td className="px-4 py-3 text-sm text-gray-600">{enc.fecha}</td>
                  <td className="px-4 py-3 text-sm text-gray-600">
                    {enc.hora_inicio} – {enc.hora_fin}
                  </td>
                  <td className="px-4 py-3">
                    <span
                      className={`inline-flex rounded-full px-2 py-0.5 text-xs font-medium ${ESTADO_COLORS[enc.estado]}`}
                    >
                      {enc.estado}
                    </span>
                  </td>
                  <td className="px-4 py-3 text-sm">
                    {enc.meet_url && (
                      <a
                        href={enc.meet_url}
                        target="_blank"
                        rel="noreferrer"
                        className="text-blue-600 hover:underline"
                      >
                        Meet
                      </a>
                    )}
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
